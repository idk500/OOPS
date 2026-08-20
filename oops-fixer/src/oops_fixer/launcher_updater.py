"""启动器更新:探测最新版本,下载并替换本地启动器

两种形态按 .venv 是否存在选择(pick_launcher):
  - 原始启动器 OneDragon-Launcher.exe(依赖项目 .venv)
  - 集成启动器 OneDragon-RuntimeLauncher.exe(自带运行时,不需要 .venv)

版本对比逻辑与主程序一致:运行启动器 --version 读取当前版本,与 CNB 最新稳定 tag 对比,
不一致就从 CNB release 下载对应 zip 替换。旧 exe 备份为 .bak(与主程序「资源下载」页备份逻辑一致)。
"""

from __future__ import annotations

import contextlib
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from oops_fixer import const
from oops_fixer.logging_utils import make_logger


def _log(message: str) -> None:
    """输出一行日志到文件(UI 由 logging 回调统一转发)。"""
    logger = make_logger()
    logger.info('%s', message)


def _log_error(message: str, exc: BaseException) -> None:
    """输出一行错误日志。"""
    logger = make_logger()
    logger.error('%s: %s', message, exc, exc_info=True)


def _decode_output(raw_output: bytes) -> str:
    """按常见 Windows 编码解码启动器输出。

    PyInstaller console 程序在不同系统代码页下输出编码可能不同,不能直接用 text=True。
    """
    for encoding in ('utf-8', 'gbk', 'mbcs'):
        try:
            return raw_output.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_output.decode('utf-8', errors='ignore')


def get_launcher_version(launcher_exe: Path) -> str:
    """读取启动器当前版本号。

    与主程序一致:运行 `OneDragon-Launcher.exe --version`,输出形如
    「绝区零 一条龙 启动器 v2.5.1」,取最后一个字段。

    Args:
        launcher_exe: 启动器 exe 路径

    Returns:
        版本号(如 v2.5.1);读取失败时返回空字符串
    """
    if not launcher_exe.is_file():
        return ''
    try:
        env = os.environ.copy()
        env.update({
            '__COMPAT_LAYER': 'RunAsInvoker',
            'PYINSTALLER_RESET_ENVIRONMENT': '1',
        })
        result = subprocess.run(
            [str(launcher_exe), '--version'],
            capture_output=True, text=False, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=env,
        )
        raw_output = result.stdout or b''
        output = _decode_output(raw_output).strip()
        if not output:
            return ''
        parts = output.split()
        return parts[-1] if parts else ''
    except Exception as exc:
        _log_error(f'读取启动器版本失败: {launcher_exe.name}', exc)
        return ''


def resolve_target_version(project_root: Path) -> str | None:
    """探测要更新的目标版本:CNB 最新稳定 tag,没有稳定版则用最新 tag。

    Args:
        project_root: 项目根目录

    Returns:
        目标版本号;探测失败时返回 None(上层决定跳过更新)
    """
    from oops_fixer import git_ops
    tags = git_ops.get_latest_tags()
    if not tags:
        return None

    for tag in tags:
        if 'beta' not in tag and 'rc' not in tag:
            return tag
    return tags[0]


def pick_launcher(project_root: Path) -> tuple[str, str] | None:
    """按启动器 exe 文件名选择要更新/打开的形态。

    只区分两种启动器,各对应 CNB 上一个包:
      - OneDragon-Launcher.exe        -> ZenlessZoneZero-OneDragon-Launcher.zip(原始版)
      - OneDragon-RuntimeLauncher.exe -> ZenlessZoneZero-OneDragon-RuntimeLauncher.zip(集成版)
    哪个存在用哪个;两个都在时用 .venv 决胜(有 .venv 说明主用原始版);
    都不存在返回 None(没有可更新的启动器)。

    Args:
        project_root: 项目根目录

    Returns:
        (exe 文件名, release zip 文件名);没有启动器时返回 None
    """
    has_original = (project_root / const.LAUNCHER_EXE_NAME).is_file()
    has_runtime = (project_root / const.RUNTIME_LAUNCHER_EXE_NAME).is_file()

    if has_original and has_runtime:
        if (project_root / '.venv').is_dir():
            return const.LAUNCHER_EXE_NAME, const.LAUNCHER_ZIP_NAME
        return const.RUNTIME_LAUNCHER_EXE_NAME, const.RUNTIME_LAUNCHER_ZIP_NAME
    if has_original:
        return const.LAUNCHER_EXE_NAME, const.LAUNCHER_ZIP_NAME
    if has_runtime:
        return const.RUNTIME_LAUNCHER_EXE_NAME, const.RUNTIME_LAUNCHER_ZIP_NAME
    return None


def update_launcher(project_root: Path, target_version: str, exe_name: str, zip_name: str) -> bool:
    """把本地启动器更新到目标版本。

    Args:
        project_root: 项目根目录
        target_version: 目标版本(如 v2.5.1)
        exe_name: 启动器 exe 文件名(原始/集成)
        zip_name: 对应的 release zip 文件名

    Returns:
        True 表示已更新或已是最新;False 表示下载失败(上层决定是否致命)
    """
    launcher_exe = project_root / exe_name
    current_version = get_launcher_version(launcher_exe)
    if current_version == target_version:
        _log(f'{exe_name} 已是最新版本 {target_version},跳过更新')
        return True

    if current_version:
        _log(f'当前 {exe_name} 版本 {current_version},目标版本 {target_version},开始更新...')
    else:
        _log(f'未检测到 {exe_name} 版本,目标版本 {target_version},开始下载...')

    zip_path = _download_launcher_zip(project_root, target_version, zip_name)
    if zip_path is None:
        return False

    try:
        _replace_launcher(project_root, zip_path, exe_name)
    finally:
        with contextlib.suppress(OSError):
            zip_path.unlink()

    new_version = get_launcher_version(launcher_exe)
    if new_version == target_version:
        _log(f'{exe_name} 更新完成,当前版本 {new_version}')
        return True
    _log(f'{exe_name} 已替换,但版本读取异常(当前 {new_version or "未知"}),请手动确认')
    return True


def _download_launcher_zip(project_root: Path, target_version: str, zip_name: str) -> Path | None:
    """按版本下载启动器压缩包,404 时按 tag 降序回退探测可用版本。

    Args:
        project_root: 项目根目录
        target_version: 首选目标版本
        zip_name: release zip 文件名

    Returns:
        下载好的 zip 文件路径;全部失败时返回 None
    """
    from oops_fixer import git_ops

    candidates = [target_version] + [t for t in git_ops.get_latest_tags() if t != target_version]
    # 不重复
    seen: set[str] = set()
    ordered: list[str] = []
    for tag in candidates:
        if tag not in seen:
            seen.add(tag)
            ordered.append(tag)

    last_error: Exception | None = None
    for tag in ordered:
        url = _build_zip_url(tag, zip_name)
        _log(f'尝试下载: {tag} {zip_name}')
        try:
            return _download_file(url, project_root, zip_name)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 404:
                _log('该版本没有启动器安装包(404),尝试下一个版本')
                continue
            _log_error(f'下载失败(HTTP {exc.code})', exc)
            break
        except Exception as exc:
            last_error = exc
            _log_error('下载失败', exc)
            break

    _log_error('启动器下载失败,未更新', last_error or RuntimeError('无可用版本'))
    return None


def _build_zip_url(tag: str, zip_name: str) -> str:
    """构造启动器压缩包的 CNB release 直链地址。"""
    return f'{const.CNB_RELEASE_DOWNLOAD_BASE}/{tag}/{zip_name}'


def _download_file(url: str, project_root: Path, zip_name: str) -> Path:
    """下载文件到项目根目录的临时文件,校验是合法 zip 后返回路径。

    Args:
        url: 下载地址
        project_root: 项目根目录
        zip_name: release zip 文件名(用于临时文件命名)

    Returns:
        下载好的 zip 文件路径

    Raises:
        urllib.error.HTTPError / OSError: 下载失败时抛出
    """
    temp_path = project_root / f'.oops_download_{zip_name}.tmp'
    try:
        _log('开始下载...')
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'OneDragon-Oops/1.0')]
        with opener.open(url, timeout=const.DOWNLOAD_TIMEOUT) as response, temp_path.open('wb') as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)

        # 校验 zip 是否完整可用
        try:
            with zipfile.ZipFile(temp_path) as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise RuntimeError(f'压缩包损坏: 成员 {bad}')
        except (zipfile.BadZipFile, RuntimeError):
            temp_path.unlink(missing_ok=True)
            raise
        _log('下载完成')
        return temp_path
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _replace_launcher(project_root: Path, zip_path: Path, exe_name: str) -> None:
    """解压 zip 替换启动器:旧 exe 备份为 .bak,新 exe 替换进来。

    Args:
        project_root: 项目根目录
        zip_path: 下载好的 zip 文件
        exe_name: 启动器 exe 文件名(原始/集成)

    Raises:
        RuntimeError: 替换失败时抛出
    """
    launcher_exe = project_root / exe_name
    backup_path = project_root / (exe_name + const.LAUNCHER_BACKUP_SUFFIX)

    # 解压到临时目录,校验内容后替换,避免替换失败导致启动器缺失
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        exe_member = _find_exe_member(names, exe_name)
        if exe_member is None:
            raise RuntimeError(f'压缩包里没有找到 {exe_name}')

        temp_dir = Path(tempfile.mkdtemp(prefix='oops_launcher_'))
        try:
            target = temp_dir / exe_member
            zf.extract(exe_member, temp_dir)
            new_exe = target

            # 校验解压出的 exe 是否真的是 Windows 可执行文件(MZ 头)
            _check_mz_header(new_exe)

            # 备份旧 exe(已存在则覆盖)
            if backup_path.exists():
                backup_path.unlink()
            if launcher_exe.exists():
                launcher_exe.replace(backup_path)
                _log(f'旧启动器已备份: {backup_path.name}')

            # 替换
            shutil.copy2(new_exe, launcher_exe)
            _log(f'新启动器已替换: {launcher_exe.name}')
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def _find_exe_member(names: list[str], exe_name: str) -> str | None:
    """在 zip 成员里找到目标启动器 exe(支持压缩包带顶层目录)。"""
    target = exe_name.lower()
    for name in names:
        if name.replace('\\', '/').lower().endswith(target):
            return name
    return None


def _check_mz_header(exe_path: Path) -> None:
    """校验文件是否以 MZ 头开头,不是则抛出。"""
    with exe_path.open('rb') as f:
        head = f.read(2)
    if head != b'MZ':
        raise RuntimeError(f'下载的启动器文件不是有效的 Windows 可执行文件: {exe_path.name}')
