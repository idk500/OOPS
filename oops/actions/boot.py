"""
oops boot —— 作为 OneDragon-Launcher.exe 的引导(默认双击运行)

设计要点(与启动器解耦):
  - OOPS 用**专用 remote `oops-cnb`** 指向 CNB 镜像来 fetch/比对/对齐,
    **完全不碰 `origin`**。OneDragon 启动器同步后会用 `_restore_origin()`
    把 origin 恢复成 primary(github)——那是它的事,OOPS 不参与争夺。
  - 新鲜度缓存只看时间戳(窗口内直接启动,不联网);不看 origin。

流程:
  1. 缓存命中(窗口内) → 跳过检查,直接启动 launcher
  2. 否则 fetch `oops-cnb` 比对:落后 → 倒数 5 秒 → 对齐(备份 + reset)
  3. 启动 OneDragon-Launcher.exe(detached),OOPS 随即退出
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

from oops.actions import git_ops
from oops.actions.mirror import MIRROR_URLS

CNB_URL = MIRROR_URLS["cnb"]
OOPS_CNB_REMOTE = "oops-cnb"  # OOPS 专用 remote,与启动器的 origin 互不干扰

CACHE_FILE = ".oops_boot_checked"
FRESH_WINDOW = 6 * 3600  # 默认 6 小时内认为已最新,跳过联网检查
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
    """缓存是否在窗口内。只看时间戳,不看 origin(避免与启动器争夺 origin)。"""
    cp = _cache_path(path)
    if not cp.exists():
        return False
    try:
        ts = float(cp.read_text(encoding="utf-8").strip())
        return time.time() - ts < window
    except Exception:
        return False


def mark_fresh(path: str) -> None:
    try:
        _cache_path(path).write_text(str(time.time()), encoding="utf-8")
    except Exception as e:
        print(f"[!] 无法写入新鲜度缓存({CACHE_FILE}): {e}")


def ensure_cnb_remote(path: str) -> None:
    """确保 OOPS 专用 remote `oops-cnb` 指向 CNB;不碰 origin。"""
    remotes = git_ops.list_remotes(path)
    cur = remotes.get(OOPS_CNB_REMOTE, {}).get("fetch")
    if cur == CNB_URL:
        return
    if OOPS_CNB_REMOTE in remotes:
        git_ops.set_remote_url(path, OOPS_CNB_REMOTE, CNB_URL)
    else:
        git_ops.set_remote_url(path, OOPS_CNB_REMOTE, CNB_URL, add=True)


def cnb_behind(path: str) -> Tuple[bool, Optional[str]]:
    """fetch oops-cnb 并比对。返回 (是否落后, 对齐目标如 'oops-cnb/main')。"""
    fr = git_ops.run_git(
        ["fetch", OOPS_CNB_REMOTE, "--prune", "--tags"],
        cwd=path,
        timeout=git_ops.FETCH_TIMEOUT,
    )
    if fr.returncode != 0:
        print(f"[!] fetch {OOPS_CNB_REMOTE} 失败,跳过本次更新检查。")
        print(f"    {fr.stderr.strip() or fr.stdout.strip()}")
        return False, None
    branch = git_ops.current_branch(path) or "main"
    target = f"{OOPS_CNB_REMOTE}/{branch}"
    if not git_ops.verify_ref(path, target):
        target = f"{OOPS_CNB_REMOTE}/HEAD"
        if not git_ops.verify_ref(path, target):
            print(f"[!] 无法解析 {OOPS_CNB_REMOTE} 的 HEAD,跳过更新检查。")
            return False, None
    local = git_ops.run_git(["rev-parse", "HEAD"], cwd=path, timeout=15).stdout.strip()
    remote = git_ops.run_git(["rev-parse", target], cwd=path, timeout=15).stdout.strip()
    return local != remote, target


def _align(path: str, target: str) -> None:
    """备份后对齐到 target(不改动分支的 upstream 跟踪,避免干扰启动器的 origin 跟踪)。"""
    from oops.actions.sync import backup_tag

    bk = backup_tag()
    git_ops.run_git(["branch", bk], cwd=path, timeout=15)
    if git_ops.is_dirty(path):
        git_ops.run_git(["stash", "push", "-u", "-m", bk], cwd=path, timeout=60)
    git_ops.run_git(["reset", "--hard", target], cwd=path, timeout=300)
    git_ops.run_git(["clean", "-fd"], cwd=path, timeout=60)
    print(f"[备份] 备份分支: {bk}(回滚: git reset --hard {bk})")


def launch(launcher: Path) -> bool:
    """detached 启动 launcher,OOPS 可独立退出。"""
    print(f"[*] 启动 {launcher.name} ...")
    flags = 0
    if hasattr(subprocess, "DETACHED_PROCESS"):
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
    """引导:必要时经 CNB 自检/更新,然后启动 OneDragon-Launcher.exe。

    返回: 0=已启动 launcher(OOPS 应退出); 1=未找到/未能启动 launcher; 2=非 git。
    """
    from oops.actions.self_update import _countdown_apply

    if not git_ops.ensure_git_or_report():
        return 3
    if not git_ops.is_git_repo(path):
        print(f"[ERROR] {path} 不是 git 仓库,无法 boot。")
        return 2

    launcher = find_launcher(path)
    if not launcher:
        print(f"[!] 未在 {path} 找到 OneDragon-Launcher.exe。")
        return 1

    # 新鲜度缓存:窗口内直接启动(不联网、不看 origin)
    if is_fresh(path):
        print(f"[*] 近期已确认最新({CACHE_FILE}),跳过自检。")
        print()
        launch(launcher)
        return 0

    ensure_cnb_remote(path)
    print(f"[*] 检查一条龙更新状态(源: CNB,专用 remote {OOPS_CNB_REMOTE})...")
    behind, target = cnb_behind(path)
    if not behind:
        print("[*] 一条龙已是最新。")
        mark_fresh(path)
        print()
        launch(launcher)
        return 0

    print("[*] 检测到本地落后于最新 HEAD。")
    if not _countdown_apply(5):
        print("[*] 已跳过更新,直接启动。")
        print()
        launch(launcher)
        return 0

    print(f"[*] 对齐到 {target}(自动备份后硬重置)...")
    _align(path, target)
    print("[完成] 已对齐到最新。")
    mark_fresh(path)
    print()
    launch(launcher)
    return 0
