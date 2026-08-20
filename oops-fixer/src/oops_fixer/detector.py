"""项目根目录校验与本项目进程清理

兜底修复器要求用户 100% 放在项目根目录运行:检测不到项目标识直接报错。
"""

from __future__ import annotations

import os
from pathlib import Path

import psutil

from oops_fixer import const
from oops_fixer.logging_utils import make_logger


class ProjectRootError(RuntimeError):
    """项目根目录校验失败的异常。"""


def _validate_project_root(root: Path) -> None:
    """校验目录是否为项目根目录,不是则抛 ProjectRootError。"""
    has_launcher = any((root / name).is_file() for name in const.PROJECT_MARKER_FILES)
    has_config = (root / 'config' / 'project.yml').is_file() and (root / '.git').exists()
    if has_launcher or has_config:
        return

    raise ProjectRootError(
        '没有在绝区零一条龙项目根目录运行!\n'
        f'当前目录: {root}\n'
        '请把本程序放在项目根目录(和 OneDragon-Launcher.exe 同一个文件夹)后重新运行。'
    )


def kill_project_processes(project_root: Path) -> list[str]:
    """结束占用项目文件的本项目进程,避免文件锁导致替换失败。

    只处理本项目的相关进程,绝不误伤其他软件:
      - OneDragon-Launcher / OneDragon-RuntimeLauncher(可能由兜底修复器改名后仍在运行)
      - OneDragon-Installer(安装器)
      - OneDragon-Updater / zzzod-updater(更新器)
      - .venv 下的 python(主程序运行时)
      - 当前进程自身除外

    Args:
        project_root: 项目根目录

    Returns:
        被杀掉的进程可执行文件路径列表
    """
    logger = make_logger()
    self_pid = os.getpid()
    killed: list[str] = []

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['pid'] == self_pid:
                continue
            name = (proc.info['name'] or '').lower()
            if name == 'onedragon-oops.exe':
                continue
            exe_path = proc.info['exe']
            if exe_path is not None and Path(exe_path).resolve() == Path(os.sys.executable).resolve():
                continue
            if not _is_project_related(name, exe_path, project_root):
                continue
            proc.kill()
            proc.wait(timeout=5)
            killed.append(exe_path or name)
            logger.info('已结束本项目进程: %s', exe_path or name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            # 进程可能已自行退出或权限不足,继续处理下一个
            continue

    if killed:
        logger.info('共结束 %d 个本项目进程', len(killed))
    return killed


def _is_project_related(name: str, exe_path: str | None, project_root: Path) -> bool:
    """判断进程是否属于本项目。"""
    if name.startswith('onedragon-'):
        return True
    if name in {'zzzod-updater.exe', 'onedragon-updater.exe'}:
        return True
    # .venv 下的 python:主程序运行时由 venv 里的 pythonw 启动
    if name in {'python.exe', 'pythonw.exe'} and exe_path:
        try:
            if Path(exe_path).is_relative_to(project_root / '.venv'):
                return True
        except ValueError:
            return False
    return False


def sys_exe_dir() -> Path:
    """返回当前可执行文件所在目录。"""
    return Path(os.path.dirname(os.path.abspath(os.sys.executable)))


def is_frozen() -> bool:
    """判断是否打包为 exe 运行。"""
    return bool(getattr(os.sys, 'frozen', False))
