"""
快速结构化诊断(诊断驱动主流程的入口)

按 SPEC v0.7.0:双击后先做秒级诊断,产出「硬阻塞 blockers + 可用代码源」,
- 有硬阻塞 → 上层弹窗(把原因明明白白告诉用户);
- 否则 → 用可达源里最优的一个(CNB>Gitee>GitHub)去强更+启动。

覆盖场景矩阵的高频项:系统版本/架构、网络(CNB/Gitee/GitHub 三源)、git 可用性、
项目位置(launcher 在不在)、磁盘/路径(中文/写权限/空间)。其余细项按 v0.8.0 补。
"""

import platform
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from oops.actions import git_ops
from oops.actions.boot import find_launcher

# 代码源探测地址(主页,够判断连通性即可)
SOURCE_PROBES = {
    "cnb": "https://cnb.cool",
    "gitee": "https://gitee.com",
    "github": "https://github.com",
}
# 源优先级(国内首选 CNB,其次 Gitee,最后 GitHub)
SOURCE_PRIORITY = ["cnb", "gitee", "github"]

MIN_FREE_GB = 1.0  # 项目目录至少留 1GB(一条龙本体更大,这里只是兜底门槛)


@dataclass
class Diagnosis:
    blockers: List[str] = field(default_factory=list)  # 硬阻塞(中文,可直接给用户看)
    warnings: List[str] = field(default_factory=list)  # 软警告
    sources_reachable: List[str] = field(
        default_factory=list
    )  # ["cnb","gitee","github"] 子集
    git_ok: bool = False
    launcher: Optional[Path] = None
    is_git_repo: bool = False

    @property
    def ok(self) -> bool:
        return not self.blockers

    def best_source(self) -> Optional[str]:
        for s in SOURCE_PRIORITY:
            if s in self.sources_reachable:
                return s
        return None


def _check_system() -> List[str]:
    """系统版本/架构。"""
    blockers: List[str] = []
    if sys.platform != "win32":
        blockers.append(f"OOPS 需要在 Windows 上运行(当前系统:{platform.system()})")
        return blockers
    try:
        major = sys.getwindowsversion().major  # type: ignore[attr-defined]
    except Exception:
        major = 10
    if major < 10:
        blockers.append(f"系统版本过低,需要 Windows 10 64 位及以上(当前主版本 {major})")
    return blockers


def _probe(url: str, timeout: float = 3.0) -> bool:
    """探测一个 URL 是否可达(只看能不能连上,不在乎状态码)。"""
    try:
        import requests

        r = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        r.close()
        return True
    except Exception:
        return False


def _check_network(reporter):
    """探测三个代码源。返回 (可达列表, blockers)。"""
    reachable: List[str] = []
    for name, url in SOURCE_PROBES.items():
        ok = _probe(url)
        reporter(f"网络探测 {name.upper()} ({url}) ... {'OK' if ok else '不可达'}")
        if ok:
            reachable.append(name)
    blockers: List[str] = []
    if not reachable:
        blockers.append(
            "无法访问任何代码源(CNB / Gitee / GitHub 都不可达),请检查网络 / 代理 / 防火墙后重试"
        )
    return reachable, blockers


def _check_git(reporter) -> bool:
    """确保 git 可用(系统 git 或自动 MinGit)。"""
    from oops.actions.git_provider import ensure_git

    binp = ensure_git(reporter)
    return bool(binp)


def _check_disk_path(path: str) -> List[str]:
    """磁盘空间 / 中文路径 / 写权限。"""
    blockers: List[str] = []
    p = Path(path)
    # 中文/特殊字符
    try:
        str(p).encode("ascii")
    except UnicodeEncodeError:
        blockers.append(
            "路径含中文或特殊字符,请把整个文件夹移到纯英文路径(如 D:/ZZZ-1D)"
        )
    # 写权限
    try:
        t = p / ".oops_write_test"
        t.write_text("ok", encoding="utf-8")
        t.unlink()
    except Exception:
        blockers.append("当前目录无写权限,请移出 Program Files,或以管理员身份运行")
    # 磁盘空间
    try:
        free_gb = shutil.disk_usage(str(p)).free / (1024**3)
        if free_gb < MIN_FREE_GB:
            blockers.append(f"磁盘空间不足(剩余 {free_gb:.1f} GB),一条龙约需数 GB 空间")
    except Exception:
        pass
    return blockers


def run_diagnosis(path: str, reporter=print) -> Diagnosis:
    """对目标目录跑一遍快速诊断,返回结构化结果(含 blockers / 可用源)。"""
    diag = Diagnosis()

    # 1. 系统
    diag.blockers += _check_system()

    # 2. 网络(决定可用源)
    reachable, net_blockers = _check_network(reporter)
    diag.sources_reachable = reachable
    diag.blockers += net_blockers

    # 3. git
    diag.git_ok = _check_git(reporter)
    if not diag.git_ok:
        diag.blockers.append(
            "无法获取可用的 git(系统未安装 git 且自动下载 MinGit 失败),请检查网络或手动安装 git"
        )

    # 4. 项目状态
    diag.launcher = find_launcher(path)
    diag.is_git_repo = git_ops.is_git_repo(path)
    if diag.launcher is None:
        diag.blockers.append(
            "未找到 OneDragon-Launcher.exe。请把 oops.exe 放到【一条龙根目录】"
            "(和 OneDragon-Launcher.exe 同级)后重试"
        )
    if diag.launcher is not None and not diag.is_git_repo:
        diag.blockers.append(
            "当前目录不像一条龙项目(不是 git 仓库)。请确认 oops.exe 在一条龙根目录"
        )

    # 5. 磁盘/路径
    diag.blockers += _check_disk_path(path)

    return diag
