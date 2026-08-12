"""
Git 提供者:保证有 git 可用

优先级:
  1. 系统 git(`git --version` 能跑)→ 直接用
  2. 缓存的自带 MinGit(`~/.oops/mingit`)→ 用它
  3. 都没有 → 从国内镜像下载 MinGit(华为云主 / npmmirror 备)→ 解压到缓存 → 用
  4. 下载也失败 → 返回 None(调用方提示用户手动装 git)

目的:一条龙用户机器上通常没有系统 git(一条龙用 pygit2),OOPS 也能自包含运行。
下载源经实测:华为云 4.8MB/s、npmmirror 完整镜像;ghfast 代理不可靠,不用。
"""

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional

import requests

from oops.actions import git_ops

NPMMIRROR_BASE = "https://registry.npmmirror.com/-/binary/git-for-windows"
HUAWEICLOUD_BASE = "https://mirrors.huaweicloud.com/git-for-windows"

# 钉版回退:npmmirror 版本列表拿不到时,直接用已确认可下的版本+资产名。
# 这样只要华为云/淘宝任一镜像通就能下到 git(不依赖列表接口)。
PINNED_FALLBACK = ("v2.43.0.windows.1", "MinGit-2.43.0-64-bit.zip")


def system_git_available() -> bool:
    try:
        r = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            timeout=8,
            encoding="utf-8",
            errors="replace",
        )
        return r.returncode == 0
    except Exception:
        return False


def _list_versions() -> List[str]:
    """npmmirror 上 git-for-windows 的稳定版本目录(如 v2.55.0.windows.3)。"""
    r = requests.get(f"{NPMMIRROR_BASE}/", timeout=15)
    r.raise_for_status()
    data = r.json()
    names = [x.get("name", "").rstrip("/") for x in data]
    stable = [
        n
        for n in names
        if n.startswith("v")
        and ".windows." in n
        and "rc" not in n.lower()
        and "pre" not in n.lower()
    ]
    return stable


def _list_assets(version: str) -> List[str]:
    r = requests.get(f"{NPMMIRROR_BASE}/{version}/", timeout=15)
    r.raise_for_status()
    return [x.get("name", "") for x in r.json()]


def _pick_mingit_asset(assets: List[str]) -> Optional[str]:
    """选 MinGit-<ver>-64-bit.zip(排除 busybox / 32-bit)。"""
    for a in assets:
        low = a.lower()
        if (
            a.startswith("MinGit-")
            and a.endswith("-64-bit.zip")
            and "busybox" not in low
        ):
            return a
    return None


def _download_candidates(version: str, asset: str) -> List[str]:
    """下载源候选(华为云最快且支持 range;npmmirror 走 CDN 跳转)。"""
    return [
        f"{HUAWEICLOUD_BASE}/{version}/{asset}",
        f"{NPMMIRROR_BASE}/{version}/{asset}",
    ]


def download_mingit(progress=print) -> Optional[str]:
    """下载并解压最新稳定版 MinGit 到缓存。成功返回 git 二进制路径,失败 None。"""
    version = None
    asset = None
    # 优先:npmmirror 列表自动取最新稳定版
    try:
        versions = _list_versions()
        if versions:
            version = versions[-1]
            asset = _pick_mingit_asset(_list_assets(version))
    except Exception as e:
        progress(f"[!] 自动获取 MinGit 版本失败({e}),改用固定版本。")
    # 回退:钉版(不依赖列表接口)
    if not version or not asset:
        version, asset = PINNED_FALLBACK
        progress(f"[*] 使用固定版本 {version}/{asset}")
    else:
        progress(f"[*] 选用 MinGit: {version}/{asset}")

    tmp_zip = None
    for url in _download_candidates(version, asset):
        try:
            progress(f"[*] 下载: {url}")
            with requests.get(url, stream=True, timeout=180) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("Content-Length", 0))
                done = 0
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                    tmp_zip = tmp.name
                    for chunk in resp.iter_content(chunk_size=1 << 16):
                        if chunk:
                            tmp.write(chunk)
                            done += len(chunk)
                            if total:
                                progress(
                                    f"\r[*] 下载进度: {done * 100 // total}% "
                                    f"({done // 1024}KB/{total // 1024}KB)",
                                    end="",
                                )
            progress()
            break
        except Exception as e:
            progress(f"\n[!] 该源失败: {e}")
            if tmp_zip:
                try:
                    os.unlink(tmp_zip)
                except OSError:
                    pass
                tmp_zip = None
            continue
    if not tmp_zip:
        return None

    target = git_ops.mingit_dir()
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    progress(f"[*] 解压到 {target} ...")
    try:
        with zipfile.ZipFile(tmp_zip) as zf:
            zf.extractall(target)
    except Exception as e:
        progress(f"[!] 解压失败: {e}")
        return None
    finally:
        try:
            os.unlink(tmp_zip)
        except OSError:
            pass

    binp = git_ops.mingit_bin_path()
    if binp.exists():
        return str(binp)
    progress(f"[!] 解压后未找到 {binp}")
    return None


def ensure_git(progress=print) -> Optional[str]:
    """确保 git 可用。成功返回二进制路径并登记到 git_ops;失败返回 None。"""
    # 1. 系统 git
    if system_git_available():
        git_ops.set_resolved_git("git")
        return "git"
    # 2. 缓存 MinGit(验证可跑)
    cached = git_ops.mingit_bin_path()
    if cached.exists():
        try:
            r = subprocess.run(
                [str(cached), "--version"],
                capture_output=True,
                timeout=8,
                encoding="utf-8",
                errors="replace",
            )
            if r.returncode == 0:
                git_ops.set_resolved_git(str(cached))
                return str(cached)
        except Exception:
            pass
    # 3. 下载
    progress("[*] 未检测到系统 git,自动下载 MinGit(国内镜像)...")
    binp = download_mingit(progress)
    if binp:
        git_ops.set_resolved_git(binp)
    return binp
