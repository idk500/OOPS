"""
oops self-update —— 更新 OOPS 自身

- 打包成 exe 的用户:从 GitHub release 下载最新 oops-windows-x64_*.zip 并替换
  (Windows 上不能覆盖运行中的 exe,先把当前 oops.exe 重命名为 oops.exe.old,
   下次启动时清理)。可用 --url 指向 CNB 镜像(zzz1d/oops)的 zip 直链。
- 源码运行的用户:git pull(可从 CNB 镜像 zzz1d/oops 拉)。
"""

import argparse
import logging
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

GITHUB_RELEASES_API = "https://api.github.com/repos/idk500/OOPS/releases/latest"
# CNB 上 OOPS 的镜像仓(供 self-update 拉取/克隆,国内更快)
CNB_OOPS_MIRROR = "https://cnb.cool/zzz1d/oops.git"


def is_frozen() -> bool:
    """纯函数:是否运行在 PyInstaller 打包环境中。"""
    return getattr(sys, "frozen", False)


def install_dir() -> Path:
    """返回 OOPS 的安装目录(exe 所在目录 / 源码仓库根)。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    # 源码: 本文件位于 <repo>/oops/actions/self_update.py
    return Path(__file__).resolve().parent.parent.parent


def normalize_tag(tag: str) -> str:
    return (tag or "").lstrip("v")


def version_tuple(v: str) -> Tuple[int, ...]:
    """纯函数:'v1.2.3' -> (1,2,3),非法段按 0。"""
    parts = []
    for p in normalize_tag(v).split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def is_newer(remote_tag: str, local_version: str) -> bool:
    return version_tuple(remote_tag) > version_tuple(local_version)


def fetch_latest_release(api_url: Optional[str]):
    """查询 release。返回 (tag_name, zip_download_url);失败返回 None。"""
    import requests

    api = api_url or GITHUB_RELEASES_API
    try:
        r = requests.get(
            api, timeout=20, headers={"Accept": "application/vnd.github+json"}
        )
    except Exception as e:
        print(f"[!] 查询最新版本异常: {e}")
        return None
    if r.status_code != 200:
        print(f"[!] 查询最新版本失败: HTTP {r.status_code}")
        return None
    data = r.json()
    tag = data.get("tag_name")
    asset_url = None
    for a in data.get("assets", []):
        name = a.get("name", "")
        if name.startswith("oops-windows-x64") and name.endswith(".zip"):
            asset_url = a.get("browser_download_url")
            break
    return tag, asset_url


def cleanup_old_exe(install: Path) -> None:
    """启动时清理上次 self-update 留下的 oops.exe.old。"""
    old = install / "oops.exe.old"
    if old.exists():
        try:
            old.unlink()
            print(f"[*] 已清理旧版本残留: {old.name}")
        except OSError as e:
            logger.debug("清理 %s 失败: %s", old, e)


def _countdown_apply(seconds: int = 5) -> bool:
    """更新前的安全倒数;用户可在期间 Ctrl+C 取消。返回 True 表示继续。"""
    import time

    print(f"[*] {seconds} 秒后开始更新(按 Ctrl+C 取消)...")
    try:
        for i in range(seconds, 0, -1):
            print(f"\r[*] 倒数 {i} ", end="", flush=True)
            time.sleep(1)
        print("\r[+] 开始更新。      ")
        return True
    except KeyboardInterrupt:
        print("\n[!] 用户取消更新。")
        return False


def _run_source_pull(args: argparse.Namespace) -> int:
    from oops.actions import git_ops

    repo_dir = install_dir()
    print(f"[*] 源码模式: git -C {repo_dir} pull")
    if not git_ops.ensure_git_or_report():
        return 3
    if not git_ops.is_git_repo(str(repo_dir)):
        print("[ERROR] 源码目录不是 git 仓库,无法 pull。")
        return 2
    remote = getattr(args, "remote", None) or "origin"
    fr = git_ops.run_git(
        ["fetch", remote], cwd=str(repo_dir), timeout=git_ops.FETCH_TIMEOUT
    )
    if fr.returncode != 0:
        print(f"[ERROR] fetch 失败: {fr.stderr.strip()}")
        return 1
    pr = git_ops.run_git(["pull", remote], cwd=str(repo_dir), timeout=300)
    if pr.returncode == 0:
        print(pr.stdout.strip())
        print("[完成] 源码已更新。")
        return 0
    print(f"[ERROR] pull 失败: {pr.stderr.strip() or pr.stdout.strip()}")
    return 1


def _run_exe_update(args: argparse.Namespace) -> int:
    import requests

    only_check = getattr(args, "check", False)
    url = getattr(args, "url", None)

    # --url 若是 zip 直链,直接用;否则视为 release API 地址
    if url and url.endswith(".zip"):
        tag = None
        zip_url = url
        print(f"[*] 使用指定 zip 直链: {zip_url}")
    else:
        info = fetch_latest_release(url)
        if not info:
            return 1
        tag, zip_url = info
        print(f"[*] 最新版本: {tag}")
        from oops import __version__

        if not is_newer(tag, __version__):
            print("[*] 已是最新版本。")
            if not getattr(args, "force", False) and not only_check:
                return 0
        if not zip_url:
            print(
                "[ERROR] 该 release 未找到 oops-windows-x64_*.zip 资产。"
                "可用 --url 指定 zip 直链(如 CNB 镜像 zzz1d/oops 的 release)。"
            )
            return 1

    if only_check:
        return 0

    # 发现可更新:倒数 5 秒后直接应用(Ctrl+C 可取消)
    if not _countdown_apply(5):
        return 0

    print(f"[*] 下载: {zip_url}")
    tmp_path = None
    try:
        with requests.get(zip_url, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp_path = tmp.name
                for chunk in resp.iter_content(chunk_size=1 << 16):
                    if chunk:
                        tmp.write(chunk)
                        done += len(chunk)
                        if total:
                            pct = done * 100 // total
                            print(
                                f"\r[*] 下载进度: {pct}% "
                                f"({done // 1024}KB/{total // 1024}KB)",
                                end="",
                            )
            print()
        print(f"[+] 已下载: {tmp_path}")

        install = install_dir()
        with zipfile.ZipFile(tmp_path) as zf:
            names = zf.namelist()
            exe_member = None
            for n in names:
                base = os.path.basename(n)
                if base.lower().endswith(".exe") and "oops" in base.lower():
                    exe_member = n
                    break
            if not exe_member:
                print("[ERROR] zip 中未找到 oops*.exe。")
                return 1
            with tempfile.TemporaryDirectory() as exdir:
                zf.extract(exe_member, exdir)
                new_exe_src = Path(exdir) / exe_member
                target_exe = install / "oops.exe"
                if target_exe.exists():
                    old = install / "oops.exe.old"
                    if old.exists():
                        try:
                            old.unlink()
                        except OSError:
                            pass
                    try:
                        target_exe.rename(old)
                        print(f"[*] 旧 exe 已重命名为 {old.name}(下次启动后清理)")
                    except OSError as e:
                        print(f"[ERROR] 无法重命名当前 exe: {e}")
                        return 1
                shutil.copy2(new_exe_src, target_exe)
                print(f"[+] 已写入新 exe: {target_exe}")

                # 顺带刷新 configs/(若有)
                for member in names:
                    if member.startswith("configs/"):
                        zf.extract(member, exdir)
                cfg_src = Path(exdir) / "configs"
                if cfg_src.exists():
                    cfg_dst = install / "configs"
                    if cfg_dst.exists():
                        shutil.copytree(cfg_src, cfg_dst, dirs_exist_ok=True)
                        print("[+] 已刷新 configs/")
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    print()
    print("[完成] OOPS 已更新。请重新启动 oops.exe。")
    return 0


def cmd_self_update(args: argparse.Namespace) -> int:
    from oops import __version__

    print(f"[*] 当前 OOPS 版本: v{__version__}")
    print(f"[*] 运行模式: {'打包 exe' if is_frozen() else '源码'}")

    if is_frozen():
        cleanup_old_exe(install_dir())
        return _run_exe_update(args)
    return _run_source_pull(args)
