"""
oops 自动修复(默认双击运行时触发)

双击 oops.exe(无参)放进绝区零一条龙项目根目录时:
  - 若 origin 未指向 CNB 镜像 → 需要 mirror
  - 若本地落后于 origin/HEAD → 需要 sync
二者任一成立,倒数 5 秒后自动执行(用户可 Ctrl+C 取消);已是最新则跳过。

目的:用户无需命令行/子命令,丢进去双击即可把一条龙更新到最新。
"""

from argparse import Namespace
from typing import Tuple

from oops.actions import git_ops
from oops.actions.mirror import MIRROR_URLS


def _is_behind(path: str) -> bool:
    """fetch origin(CNB)后,本地 HEAD 是否落后于 origin/HEAD。"""
    fr = git_ops.run_git(
        ["fetch", "origin", "--prune", "--tags"],
        cwd=path,
        timeout=git_ops.FETCH_TIMEOUT,
    )
    if fr.returncode != 0:
        return False  # fetch 失败就不强行 sync,留给预检报告去说
    head_branch = git_ops.resolve_remote_head(path, "origin")
    target = f"origin/{head_branch}" if head_branch else "origin/HEAD"
    local = git_ops.run_git(["rev-parse", "HEAD"], cwd=path, timeout=15)
    remote = git_ops.run_git(["rev-parse", target], cwd=path, timeout=15)
    if local.returncode != 0 or remote.returncode != 0:
        return False
    return local.stdout.strip() != remote.stdout.strip()


def plan(path: str) -> Tuple[bool, bool, str]:
    """返回 (need_mirror, need_sync, 当前origin_url)。"""
    cnb_url = MIRROR_URLS["cnb"]
    origin = git_ops.get_remote_url(path, "origin") or ""
    need_mirror = bool(origin) and origin != cnb_url
    need_sync = False
    # origin 非 CNB 时不预先 fetch(可能是慢/不通的 GitHub),放到 mirror 之后
    if not need_mirror and origin == cnb_url:
        need_sync = _is_behind(path)
    return need_mirror, need_sync, origin


def auto_fix(path: str) -> int:
    """检测并在需要时自动 mirror+sync。返回 0=无需/完成,2=非 git。"""
    from oops.actions.mirror import cmd_mirror
    from oops.actions.self_update import _countdown_apply
    from oops.actions.sync import cmd_sync

    if not git_ops.is_git_repo(path):
        return 2

    need_mirror, need_sync, origin = plan(path)
    if not (need_mirror or need_sync):
        print("[*] 一条龙已是最新(origin=CNB 且已对齐 HEAD),无需自动修复。")
        return 0

    print("[*] 检测到一条龙需要更新:")
    if need_mirror:
        print(f"    - origin 未指向 CNB(当前: {origin})")
    if need_sync:
        print("    - 本地代码落后于最新 HEAD")
    print()

    if not _countdown_apply(5):
        print("[*] 已跳过自动修复。")
        return 0

    if need_mirror:
        print()
        cmd_mirror(Namespace(path=path, url=None, to="cnb", no_verify=False))
        # mirror 后 origin=CNB,再判断是否需要 sync
        need_sync = _is_behind(path)
    if need_sync:
        print()
        cmd_sync(
            Namespace(
                path=path,
                remote="origin",
                branch=None,
                no_clean=False,
                no_backup=False,
            )
        )
    print()
    print("[完成] 一条龙已更新到最新。")
    return 0
