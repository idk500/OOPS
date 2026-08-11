"""
oops boot —— 作为 OneDragon-Launcher.exe 的引导(默认双击运行)

流程:
  1. 新鲜度缓存命中(窗口内且 origin=CNB) → 跳过自检,直接启动 launcher(秒开)
  2. 否则自检/更新(auto_fix:需要时倒数 5 秒 mirror+sync) → 写缓存
  3. 启动 OneDragon-Launcher.exe(detached),OOPS 随即退出

目的:用户双击 oops.exe,自动保证代码最新后启动一条龙,无需命令行。
"""

import subprocess
import time
from pathlib import Path
from typing import Optional

from oops.actions import git_ops
from oops.actions.mirror import MIRROR_URLS

# 新鲜度缓存:窗口内认为已最新,跳过网络检查
CACHE_FILE = ".oops_boot_checked"
FRESH_WINDOW = 6 * 3600  # 默认 6 小时
# launcher 候选名(按优先级)
LAUNCHER_NAMES = ["OneDragon-Launcher.exe", "OneDragon-LauncherE.exe"]


def find_launcher(path: str) -> Optional[Path]:
    root = Path(path)
    for name in LAUNCHER_NAMES:
        p = root / name
        if p.exists():
            return p
    return None


def _cache_path(path: str) -> Path:
    return Path(path) / CACHE_FILE


def is_fresh(path: str, window: int = FRESH_WINDOW) -> bool:
    """缓存是否新鲜(窗口内且 origin 仍是 CNB)。"""
    cp = _cache_path(path)
    if not cp.exists():
        return False
    try:
        ts = float(cp.read_text(encoding="utf-8").strip())
        if time.time() - ts < window:
            # origin 必须仍是 CNB,否则缓存作废
            return git_ops.get_remote_url(path, "origin") == MIRROR_URLS["cnb"]
    except Exception:
        pass
    return False


def mark_fresh(path: str) -> None:
    try:
        _cache_path(path).write_text(str(time.time()), encoding="utf-8")
    except Exception as e:
        print(f"[!] 无法写入新鲜度缓存({CACHE_FILE}): {e}")


def launch(launcher: Path) -> bool:
    """detached 启动 launcher,OOPS 可独立退出。"""
    print(f"[*] 启动 {launcher.name} ...")
    flags = 0
    if hasattr(subprocess, "DETACHED_PROCESS"):  # Windows
        flags |= subprocess.DETACHED_PROCESS
    if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        flags |= subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        subprocess.Popen(
            [str(launcher)],
            cwd=str(launcher.parent),
            close_fds=True,
            creationflags=flags,
        )
        print(f"[+] 已启动 {launcher.name}")
        return True
    except Exception as e:
        print(f"[ERROR] 启动 {launcher.name} 失败: {e}")
        return False


def boot(path: str) -> int:
    """引导:必要时自检/更新,然后启动 OneDragon-Launcher.exe。

    返回: 0=已启动 launcher(OOPS 应退出); 1=未找到/未能启动 launcher; 2=非 git。
    """
    from oops.actions.auto_fix import auto_fix

    if not git_ops.is_git_repo(path):
        print(f"[ERROR] {path} 不是 git 仓库,无法 boot。")
        return 2

    launcher = find_launcher(path)
    if not launcher:
        print(f"[!] 未在 {path} 找到 OneDragon-Launcher.exe。")
        return 1

    # 新鲜度缓存:窗口内且 origin=CNB → 跳过自检
    if is_fresh(path):
        print(f"[*] 代码近期已确认最新({CACHE_FILE}),跳过自检。")
    else:
        print("[*] 检查一条龙更新状态...")
        status = auto_fix(path)
        # 已确认最新或已更新 → 写缓存(取消/非最新不写,下次还会检查)
        if status in ("latest", "updated"):
            mark_fresh(path)

    print()
    if launch(launcher):
        return 0
    return 1
