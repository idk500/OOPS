"""虚拟环境体检与修复

不同版本的启动器留下的 .venv 形态不一:新版用项目自带 uv + .install/python 创建,
旧版可能指向用户系统 Python(卸载后即坏)。这里统一体检并按启动器自己的方式修复:
`uv venv .venv --python=<project.yml 版本> --no-python-downloads` + `uv sync`。
修复前自动备份旧 .venv,失败时回滚,不把用户环境越修越坏。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from oops_fixer import const
from oops_fixer.logging_utils import make_logger

# 状态常量
STATUS_OK = 'ok'
STATUS_MISSING = 'missing'
STATUS_BROKEN = 'broken'
STATUS_MISMATCH = 'mismatch'


def _log(message: str) -> None:
    make_logger().info('%s', message)


def _log_error(message: str, exc: BaseException | None = None) -> None:
    logger = make_logger()
    if exc is not None:
        logger.error('%s: %s', message, exc, exc_info=True)
    else:
        logger.error('%s', message)


def check_venv(project_root: Path) -> tuple[str, str]:
    """体检虚拟环境。

    Args:
        project_root: 项目根目录

    Returns:
        (状态, 说明) —— 状态为 ok / missing / broken / mismatch
    """
    venv_dir = project_root / '.venv'
    python_exe = venv_dir / 'Scripts' / 'python.exe'
    if not venv_dir.is_dir():
        return STATUS_MISSING, '虚拟环境不存在'
    if not python_exe.is_file():
        return STATUS_BROKEN, '虚拟环境缺少 python.exe'

    cfg = venv_dir / 'pyvenv.cfg'
    if not cfg.is_file():
        return STATUS_BROKEN, '虚拟环境缺少 pyvenv.cfg'
    try:
        cfg_text = cfg.read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        return STATUS_BROKEN, f'pyvenv.cfg 读取失败: {exc}'

    # 旧版启动器的 venv 可能指向用户系统 Python;系统 Python 被卸载后 venv 即坏
    match = re.search(r'^home\s*=\s*(.+)$', cfg_text, re.MULTILINE)
    if match:
        home = Path(match.group(1).strip())
        if not home.is_dir():
            return STATUS_BROKEN, f'基础 Python 不存在(可能已被卸载): {home}'

    # 运行时体检:能跑、版本对
    result = _run([str(python_exe), '--version'], timeout=30)
    if result is None or result.returncode != 0:
        return STATUS_BROKEN, '虚拟环境里的 python 无法运行'
    version = _parse_python_version(_decode(result.stdout) + _decode(result.stderr))
    if not version:
        return STATUS_BROKEN, '无法识别虚拟环境 Python 版本'

    expected = project_python_version(project_root)
    if version != expected:
        return STATUS_MISMATCH, f'Python 版本不符: 虚拟环境 {version},项目要求 {expected}'
    return STATUS_OK, f'虚拟环境正常 (Python {version})'


def project_python_version(project_root: Path) -> str:
    """读取项目要求的主.次 Python 版本(config/project.yml 的 python_version)。"""
    try:
        text = (project_root / 'config' / 'project.yml').read_text(encoding='utf-8', errors='replace')
        match = re.search(r'^python_version:\s*["\']?(\d+(?:\.\d+)?)', text, re.MULTILINE)
        if match:
            parts = match.group(1).split('.')
            return '.'.join(parts[:2])
    except OSError:
        pass
    _log('未能读取 config/project.yml 的 python_version,按 3.11 处理')
    return '3.11'


def repair_venv(project_root: Path) -> None:
    """按启动器的方式重建虚拟环境(先备份,失败回滚)。

    Args:
        project_root: 项目根目录

    Raises:
        RuntimeError: 缺少项目自带的 uv,或任一步骤失败(已回滚备份)
    """
    uv_exe = project_root / '.install' / 'uv' / 'uv.exe'
    if not uv_exe.is_file():
        raise RuntimeError('项目缺少自带的 uv (.install/uv/uv.exe),无法在本工具内修复虚拟环境')

    venv_dir = project_root / '.venv'
    expected = project_python_version(project_root)
    pip_source = _pip_source(project_root)

    # 1. 备份旧 .venv(存在的话)
    backup: Path | None = None
    if venv_dir.exists():
        backup = project_root / f'.venv.oops-bak-{time.strftime("%Y%m%d-%H%M%S")}'
        shutil.move(str(venv_dir), str(backup))
        _log(f'旧虚拟环境已备份: {backup.name}')

    try:
        # 2. 创建虚拟环境(与启动器一致:项目自带 python,不联网下载解释器)
        base_env = os.environ.copy()
        base_env['UV_PYTHON_INSTALL_DIR'] = str(project_root / '.install' / 'python')
        _log(f'创建虚拟环境 (Python {expected},使用项目自带解释器)...')
        result = _run(
            [str(uv_exe), 'venv', str(venv_dir), f'--python={expected}', '--no-python-downloads'],
            timeout=const.VENV_OPERATION_TIMEOUT,
            env=base_env,
        )
        if result is None or result.returncode != 0:
            detail = _decode(result.stderr).strip()[-300:] if result else '无输出'
            raise RuntimeError(f'uv venv 创建失败: {detail or "返回码非 0"}')

        # 3. 安装依赖(与启动器一致:本地 wheels 优先 + pip 源兜底)
        sync_env = base_env.copy()
        sync_env['VIRTUAL_ENV'] = str(venv_dir)
        _log('安装运行依赖(本地 wheels 优先,不足部分走 pip 源)...')
        result = _run(
            [
                str(uv_exe),
                'sync',
                '--find-links',
                str(project_root / '.install' / 'wheels'),
                '--default-index',
                pip_source,
            ],
            timeout=const.VENV_OPERATION_TIMEOUT,
            env=sync_env,
            cwd=str(project_root),
        )
        if result is None or result.returncode != 0:
            detail = _decode(result.stderr).strip()[-300:] if result else '无输出'
            raise RuntimeError(f'uv sync 安装依赖失败: {detail or "返回码非 0"}')

        # 4. 复检
        status, detail = check_venv(project_root)
        if status != STATUS_OK:
            raise RuntimeError(f'重建后复检未通过: {detail}')
        _log(f'虚拟环境重建完成: {detail}')
    except Exception:
        # 失败回滚:删掉半成品,把备份放回去,不把用户环境越修越坏
        if venv_dir.exists():
            shutil.rmtree(venv_dir, ignore_errors=True)
        if backup is not None and backup.is_dir():
            shutil.move(str(backup), str(venv_dir))
            _log('重建失败,已回滚为原虚拟环境')
        raise


def _pip_source(project_root: Path) -> str:
    """读取用户配置的 pip 源(config/env.yml),没有就用阿里云。"""
    try:
        text = (project_root / 'config' / 'env.yml').read_text(encoding='utf-8', errors='replace')
        match = re.search(r'^pip_source:\s*(\S+)', text, re.MULTILINE)
        if match:
            return match.group(1)
    except OSError:
        pass
    return const.DEFAULT_PIP_SOURCE


def _run(command: list[str], timeout: float, env: dict[str, str] | None = None, cwd: str | None = None):
    """执行命令;超时/找不到程序返回 None,其余返回 CompletedProcess。"""
    try:
        return subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            env=env,
            cwd=cwd,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        _log_error(f'命令执行失败: {command[0]}', exc)
        return None


def _parse_python_version(output: str) -> str:
    """从 `Python 3.11.9` 输出中提取主.次版本。"""
    match = re.search(r'Python\s+(\d+)\.(\d+)', output)
    if match:
        return f'{match.group(1)}.{match.group(2)}'
    return ''


def _decode(raw: bytes | str) -> str:
    """按常见 Windows 编码解码子进程输出(bytes 直接返回字符串则原样)。"""
    if isinstance(raw, str):
        return raw
    for encoding in ('utf-8', 'gbk'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='ignore')
