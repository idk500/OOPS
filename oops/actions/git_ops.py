"""
Git 操作底层工具

为 mirror / sync / self-update 等写操作提供受控的 git 命令执行能力。
沿用 detectors/project_version.py 的 subprocess 风格(只读检测用)。
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60  # 普通 git 命令超时(秒)
FETCH_TIMEOUT = 600  # fetch / pull 可能较慢,尤其首次补 blob


def run_git(
    args: List[str],
    cwd: str,
    timeout: int = DEFAULT_TIMEOUT,
    check: bool = False,
) -> subprocess.CompletedProcess:
    """执行一条 git 命令。

    Args:
        args: git 子参数列表,例如 ["remote", "-v"]
        cwd: 工作目录(仓库路径)
        timeout: 超时秒数
        check: 为 True 时返回码非 0 抛出 CalledProcessError

    Returns:
        subprocess.CompletedProcess
    """
    cmd = ["git"] + args
    logger.debug("run_git: %s (cwd=%s)", " ".join(cmd), cwd)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )
    return result


def is_git_repo(path: str) -> bool:
    """判断目录是否在 git 工作区内。"""
    p = Path(path)
    if not p.exists():
        return False
    r = run_git(["rev-parse", "--is-inside-work-tree"], cwd=path, timeout=10)
    return r.returncode == 0 and r.stdout.strip() == "true"


def list_remotes(path: str) -> Dict[str, Dict[str, str]]:
    """返回 {remote_name: {"fetch": url, "push": url}}。"""
    r = run_git(["remote", "-v"], cwd=path, timeout=15)
    remotes: Dict[str, Dict[str, str]] = {}
    if r.returncode != 0:
        return remotes
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            name, url, kind_paren = parts[0], parts[1], parts[2]
            kind = kind_paren.strip("()")
            remotes.setdefault(name, {})
            remotes[name][kind] = url
    return remotes


def remote_exists(path: str, name: str) -> bool:
    return name in list_remotes(path)


def get_remote_url(path: str, name: str) -> Optional[str]:
    remotes = list_remotes(path)
    info = remotes.get(name)
    if not info:
        return None
    return info.get("fetch") or info.get("push")


def set_remote_url(
    path: str, name: str, url: str, add: bool = False
) -> subprocess.CompletedProcess:
    """新增或修改一个远程的 URL。"""
    if add:
        return run_git(["remote", "add", name, url], cwd=path)
    return run_git(["remote", "set-url", name, url], cwd=path)


def rename_remote(path: str, old: str, new: str) -> subprocess.CompletedProcess:
    return run_git(["remote", "rename", old, new], cwd=path)


def current_branch(path: str) -> Optional[str]:
    r = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=path, timeout=10)
    if r.returncode == 0:
        b = r.stdout.strip()
        return b or None
    return None


def get_short_sha(path: str) -> Optional[str]:
    r = run_git(["rev-parse", "--short", "HEAD"], cwd=path, timeout=10)
    if r.returncode == 0:
        return r.stdout.strip() or None
    return None


def resolve_remote_head(path: str, remote: str) -> Optional[str]:
    """返回 remote/HEAD 指向的分支名(如 'main'),无法解析则 None。"""
    r = run_git(["symbolic-ref", f"refs/remotes/{remote}/HEAD"], cwd=path, timeout=10)
    if r.returncode != 0:
        return None
    ref = r.stdout.strip()
    prefix = f"refs/remotes/{remote}/"
    if ref.startswith(prefix):
        return ref[len(prefix) :]
    return None


def is_dirty(path: str) -> bool:
    """工作区是否有改动(含未跟踪文件)。"""
    r = run_git(["status", "--porcelain"], cwd=path, timeout=20)
    if r.returncode != 0:
        return False
    return bool(r.stdout.strip())


def verify_ref(path: str, ref: str) -> bool:
    """某个引用(如 origin/main)在本地是否存在。"""
    r = run_git(["rev-parse", "--verify", ref], cwd=path, timeout=15)
    return r.returncode == 0


def resolve_target_path(explicit_path: Optional[str] = None) -> Optional[str]:
    """解析动作命令要操作的目标仓库路径。

    优先级:explicit_path(--path) > 当前目录自动检测 > 父目录扫描。
    """
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        return str(p)
    try:
        from oops.core.project_detector import ProjectDetector

        detector = ProjectDetector()
        det = detector.detect_current_directory()
        if not det:
            det = detector.scan_parent_directories()
        if det:
            return det.get("install_path")
    except Exception as e:
        logger.debug("项目检测失败: %s", e)
    return None
