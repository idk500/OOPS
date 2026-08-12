"""
oops boot —— 作为 OneDragon-Launcher.exe 的引导(默认双击运行)

设计要点(与启动器解耦):
  - OOPS 用**专用 remote `oops-cnb`** 指向 CNB 镜像来 fetch/比对/对齐,
    **完全不碰 `origin`**。OneDragon 启动器同步后会 `_restore_origin()`
    把 origin 恢复成 primary(github)——那是它的事,OOPS 不参与争夺。
  - 新鲜度缓存只看时间戳(窗口内直接启动,不联网);不看 origin。
  - 所有输出走 `reporter`(默认 print);GUI 模式下传一个置顶窗口的方法,
    这样双击时进度/倒数/错误都显示在 GUI 窗口里,不依赖黑控制台。
  - 倒数仅作可见提示,无人值守(到点自动继续,不需要用户操作)。

失败时抛 RuntimeError(由顶层捕获 → 置顶错误窗 + 写 oops-error.txt)。
"""

import subprocess
import time
from pathlib import Path
from typing import Callable, Optional, Tuple

from oops.actions import git_ops
from oops.actions.mirror import MIRROR_URLS

CNB_URL = MIRROR_URLS["cnb"]
OOPS_CNB_REMOTE = "oops-cnb"  # OOPS 专用 remote,与启动器的 origin 互不干扰

CACHE_FILE = ".oops_boot_checked"
FRESH_WINDOW = 6 * 3600  # 默认 6 小时内认为已最新,跳过联网检查
LAUNCHER_NAMES = ["OneDragon-Launcher.exe", "OneDragon-LauncherE.exe"]

Reporter = Callable[[str], None]


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


def ensure_cnb_remote(path: str, url: str = CNB_URL) -> None:
    """确保 OOPS 专用 remote `oops-cnb` 指向给定源(默认 CNB);不碰 origin。"""
    remotes = git_ops.list_remotes(path)
    cur = remotes.get(OOPS_CNB_REMOTE, {}).get("fetch")
    if cur == url:
        return
    if OOPS_CNB_REMOTE in remotes:
        git_ops.set_remote_url(path, OOPS_CNB_REMOTE, url)
    else:
        git_ops.set_remote_url(path, OOPS_CNB_REMOTE, url, add=True)


def cnb_behind(path: str, reporter: Reporter = print) -> Tuple[bool, Optional[str]]:
    """fetch oops-cnb 并比对。返回 (是否落后, 对齐目标如 'oops-cnb/main')。"""
    fr = git_ops.run_git(
        ["fetch", OOPS_CNB_REMOTE, "--prune", "--tags"],
        cwd=path,
        timeout=git_ops.FETCH_TIMEOUT,
    )
    if fr.returncode != 0:
        reporter(f"从 CNB 拉取失败,跳过本次更新检查。")
        return False, None
    branch = git_ops.current_branch(path) or "main"
    target = f"{OOPS_CNB_REMOTE}/{branch}"
    if not git_ops.verify_ref(path, target):
        target = f"{OOPS_CNB_REMOTE}/HEAD"
        if not git_ops.verify_ref(path, target):
            reporter(f"无法解析 {OOPS_CNB_REMOTE} 的 HEAD,跳过更新检查。")
            return False, None
    local = git_ops.run_git(["rev-parse", "HEAD"], cwd=path, timeout=15).stdout.strip()
    remote = git_ops.run_git(["rev-parse", target], cwd=path, timeout=15).stdout.strip()
    return local != remote, target


def _align(path: str, target: str, reporter: Reporter = print) -> None:
    """备份后对齐到 target(不改动分支的 upstream 跟踪,避免干扰启动器的 origin)。"""
    from oops.actions.sync import backup_tag

    bk = backup_tag()
    git_ops.run_git(["branch", bk], cwd=path, timeout=15)  # 备份分支,失败不致命
    if git_ops.is_dirty(path):
        git_ops.run_git(["stash", "push", "-u", "-m", bk], cwd=path, timeout=60)
    rr = git_ops.run_git(["reset", "--hard", target], cwd=path, timeout=300)
    if rr.returncode != 0:
        raise RuntimeError(
            f"对齐失败: git reset --hard {target} 未成功。\n{rr.stderr.strip() or rr.stdout.strip()}"
        )
    git_ops.run_git(["clean", "-fd"], cwd=path, timeout=60)  # clean 失败不致命
    reporter(f"已备份(分支 {bk};回滚: git reset --hard {bk})")


def _countdown(seconds: int, reporter: Reporter = print) -> None:
    """可见倒数(无人值守:到点自动继续,不需要用户操作)。"""
    for i in range(seconds, 0, -1):
        reporter(f"{i} 秒后开始更新…")
        time.sleep(1)
    reporter("开始更新。")


def launch(launcher: Path) -> bool:
    """detached 启动 launcher,OOPS 可独立退出。"""
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
        return True
    except Exception as e:
        print(f"[ERROR] 启动 {launcher.name} 失败: {e}")
        return False


def boot(path: str, reporter: Reporter = print) -> int:
    """诊断驱动的兜底恢复:先快速诊断,硬阻塞→raise(上层弹窗);

    否则用可达源里最优的一个(CNB>Gitee>GitHub)绕过原更新链路强更,然后启动一条龙。
    完全无人值守;失败抛 RuntimeError(顶层捕获 → 置顶错误窗 + 写日志)。
    """
    from oops.actions.diagnose import run_diagnosis

    reporter("快速诊断环境与网络…")
    diag = run_diagnosis(path, reporter)
    if not diag.ok:
        raise RuntimeError(
            "无法继续,存在以下问题:\n\n" + "\n".join(f"• {b}" for b in diag.blockers)
        )

    launcher = diag.launcher  # 诊断已确认存在
    source = diag.best_source()
    if source is None:
        raise RuntimeError("没有可用的代码源(网络诊断异常),请检查网络后重试。")
    reporter(f"可用源:{source.upper()}。")

    # 新鲜度缓存:窗口内、且无新阻塞 → 直接启动
    if is_fresh(path):
        reporter("近期已确认最新,直接启动一条龙。")
        if not launch(launcher):
            raise RuntimeError(f"启动 {launcher.name} 失败。")
        return 0

    ensure_cnb_remote(path, MIRROR_URLS[source])
    reporter(f"从 {source.upper()} 检查一条龙更新状态…")
    behind, target = cnb_behind(path, reporter)
    if not behind:
        reporter("一条龙已是最新。")
        mark_fresh(path)
        if not launch(launcher):
            raise RuntimeError(f"启动 {launcher.name} 失败。")
        return 0

    reporter("检测到一条龙有更新。")
    _countdown(5, reporter)  # 可见倒数,无人值守自动继续
    reporter("正在应用更新(已备份,可回退)…")
    _align(path, target, reporter)
    reporter("已更新到最新。")
    mark_fresh(path)
    if not launch(launcher):
        raise RuntimeError(f"启动 {launcher.name} 失败。")
    return 0
