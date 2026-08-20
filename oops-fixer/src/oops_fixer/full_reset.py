"""完全重置:上次急救失败后,下载全量环境包重建到新目录

流程:结束占用进程 -> 探测最新稳定 tag -> 拼 Full-Environment.zip 直链(404 回退旧 tag)
-> 磁盘空间预检 -> 下载并校验 zip -> 解压到 <旧目录名>_MMDD(同日已存在则先删重建)
-> 迁移用户数据(根配置 yml + 最多两个账户目录,env.yml 做旧路径->新路径改写)
-> 拷贝本工具 exe 到新目录。旧目录原样保留,由上层弹窗告知用户新目录位置。
"""

from __future__ import annotations

import contextlib
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from oops_fixer import const, detector, git_ops
from oops_fixer.logging_utils import make_logger


def _log(message: str) -> None:
    """输出一行日志到文件(UI 由 logging 回调统一转发)。"""
    logger = make_logger()
    logger.info('%s', message)


def _log_error(message: str, exc: BaseException) -> None:
    """输出一行错误日志。"""
    logger = make_logger()
    logger.error('%s: %s', message, exc, exc_info=True)


def run_full_reset(project_root: Path) -> Path:
    """执行完全重置,返回重建好的新目录。

    Args:
        project_root: 旧项目根目录

    Returns:
        新项目目录(已解压、已迁移用户数据、已放入本工具 exe)

    Raises:
        RuntimeError: 任一关键步骤失败(由上层弹窗并保留日志)
    """
    # 1. 结束占用旧目录文件的进程(迁移读取配置时避免文件锁干扰)
    killed = detector.kill_project_processes(project_root)
    if killed:
        _log(f'已结束 {len(killed)} 个占用旧目录文件的进程')

    # 2. 探测目标版本并下载全量环境包(404 时按 tag 降序回退)
    zip_path = _download_full_env_zip(project_root)
    try:
        # 3. 新目录(同日已存在则先删重建,防止连续失败目录繁殖)
        new_root = _prepare_new_root(project_root)

        # 4. 解压(自动剥离压缩包顶层目录),空间不足时报错清理
        _extract_into(zip_path, new_root)

        # 5. 迁移用户数据 + 拷贝本工具 exe
        _migrate_user_data(project_root, new_root)
        _copy_self_exe(new_root)
    except Exception:
        # 失败时清掉半成品新目录,避免下次误用
        candidate = _build_new_root_path(project_root)
        if candidate.is_dir():
            shutil.rmtree(candidate, ignore_errors=True)
        raise
    finally:
        with contextlib.suppress(OSError):
            zip_path.unlink(missing_ok=True)

    _log(f'完全重置完成,新目录: {new_root}')
    return new_root


# ---- 版本与下载 ----


def _download_full_env_zip(project_root: Path) -> Path:
    """下载最新稳定版全量环境包,404 时回退旧 tag。

    Returns:
        下载并校验过的 zip 文件路径(旧目录同级的临时文件)

    Raises:
        RuntimeError: 全部候选版本都下载失败
    """
    tags = git_ops.get_latest_tags()
    if not tags:
        raise RuntimeError('无法探测远程版本标签,请检查网络后重试')

    last_error: Exception | None = None
    for tag in tags:
        zip_name = const.FULL_ENV_ZIP_TEMPLATE.format(tag=tag)
        url = f'{const.CNB_RELEASE_DOWNLOAD_BASE}/{tag}/{zip_name}'
        _log(f'尝试下载全量环境包: {tag} {zip_name}')
        try:
            return _download_and_check(url, project_root, zip_name)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 404:
                _log('该版本没有全量环境包(404),尝试上一个版本')
                continue
            raise RuntimeError(f'下载全量环境包失败(HTTP {exc.code})') from exc
        except Exception as exc:
            last_error = exc
            raise RuntimeError(f'下载全量环境包失败: {exc}') from exc

    raise RuntimeError(f'所有版本都没有可用的全量环境包: {last_error}')


def _download_and_check(url: str, project_root: Path, zip_name: str) -> Path:
    """下载文件到旧目录同级临时文件,预检磁盘空间并校验 zip 完整性。"""
    temp_path = project_root.parent / f'.oops_reset_{zip_name}.tmp'
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'OneDragon-Oops/1.0')]
    try:
        with opener.open(url, timeout=const.DOWNLOAD_TIMEOUT) as response, temp_path.open('wb') as out:
            total = int(response.headers.get('Content-Length') or 0)
            _check_disk_space(project_root.parent, total, label='下载前')
            _log(f'开始下载(约 {total / 1024 / 1024:.0f} MB)...')
            copied = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                copied += len(chunk)
                if total and copied % (64 * 1024 * 1024) < len(chunk):
                    _log(f'已下载 {copied / 1024 / 1024:.0f} / {total / 1024 / 1024:.0f} MB')

        size = temp_path.stat().st_size
        _check_disk_space(project_root.parent, int(size), factor=const.RESET_DISK_SPACE_FACTOR, label='解压前')
        try:
            with zipfile.ZipFile(temp_path) as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise RuntimeError(f'压缩包损坏: 成员 {bad}')
        except (zipfile.BadZipFile, RuntimeError):
            raise
        _log('下载完成,压缩包校验通过')
        return temp_path
    except Exception:
        with contextlib.suppress(OSError):
            temp_path.unlink(missing_ok=True)
        raise


def _check_disk_space(drive_dir: Path, zip_size: int, factor: float = 2.0, label: str = '') -> None:
    """检查目标盘剩余空间是否足够,不足则抛错(压缩包体积 * factor)。"""
    if zip_size <= 0:
        return
    free = shutil.disk_usage(str(drive_dir)).free
    need = int(zip_size * factor)
    if free < need:
        raise RuntimeError(
            f'磁盘空间不足({label}): 需要 约 {need / 1024 / 1024:.0f} MB,'
            f'{drive_dir.anchor} 仅剩 {free / 1024 / 1024:.0f} MB,请先清理磁盘'
        )


# ---- 新目录与解压 ----


def _build_new_root_path(project_root: Path) -> Path:
    """构造重置目标目录:<旧目录名>_MMDD(如 D:\\ZZZ1D -> D:\\ZZZ1D_0819)。"""
    suffix = time.strftime(const.RESET_DIR_SUFFIX_FORMAT)
    return project_root.parent / f'{project_root.name}_{suffix}'


def _prepare_new_root(project_root: Path) -> Path:
    """创建重置目标目录。

    同日目录已存在时:
    - 若像是重置完成的项目(内有 OneDragon-Launcher.exe)→ 拒绝重置,
      防止用户反复双击旧目录把正在使用的新目录删掉;
    - 若是未完成残留(没有启动器)→ 删除重建。
    """
    new_root = _build_new_root_path(project_root)
    if new_root.is_dir():
        looks_complete = (new_root / const.LAUNCHER_EXE_NAME).is_file() or (
            new_root / const.RUNTIME_LAUNCHER_EXE_NAME
        ).is_file()
        if looks_complete:
            raise RuntimeError(
                f'今日已重置过,新目录已存在且可使用:\n{new_root}\n\n'
                '请直接在新目录运行;如确需再次重置,请先手动删除该目录。'
            )
        _log(f'目标目录存在未完成残留,先删除重建: {new_root.name}')
        shutil.rmtree(new_root)
    new_root.mkdir(parents=True)
    _log(f'重置目标目录: {new_root}')
    return new_root


def _extract_into(zip_path: Path, new_root: Path) -> None:
    """解压全量包到新目录;压缩包若带单一顶层目录则自动剥掉一层壳。"""
    with tempfile.TemporaryDirectory(prefix='oops_reset_') as tmp:
        tmp_dir = Path(tmp)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmp_dir)

        content_root = tmp_dir
        entries = list(tmp_dir.iterdir())
        # 全量包通常带一层同名顶层目录(ZenlessZoneZero-OneDragon-vX-Full-Environment/)
        if len(entries) == 1 and entries[0].is_dir():
            content_root = entries[0]
            _log(f'剥离压缩包顶层目录: {content_root.name}')

        moved = 0
        for item in content_root.iterdir():
            shutil.move(str(item), str(new_root / item.name))
            moved += 1
        _log(f'已解压 {moved} 项到新目录')


# ---- 用户数据迁移 ----


def _migrate_user_data(old_root: Path, new_root: Path) -> None:
    """把用户配置与最多两个账户目录从旧目录迁到新目录。

    env.yml 里的绝对路径(python_path/git_path/uv_path 指向旧目录)统一改写为新目录。
    """
    old_config = old_root / 'config'
    new_config = new_root / 'config'
    if not old_config.is_dir():
        _log('旧目录没有 config/,跳过用户数据迁移')
        return
    new_config.mkdir(parents=True, exist_ok=True)

    # 1. 根配置文件
    migrated: list[str] = []
    for name in const.USER_CONFIG_FILES:
        src = old_config / name
        if not src.is_file():
            continue
        dest = new_config / name
        if name == 'env.yml':
            _copy_env_with_path_rewrite(src, dest, old_root, new_root)
        else:
            shutil.copy2(src, dest)
        migrated.append(name)
    if migrated:
        _log(f'已迁移用户配置: {", ".join(migrated)}')

    # 2. 账户目录:最多两个,其余不迁
    pattern = re.compile(const.USER_ACCOUNT_DIR_PATTERN)
    account_dirs = sorted(
        (d for d in old_config.iterdir() if d.is_dir() and pattern.match(d.name)),
        key=lambda d: d.name,
    )
    taken = account_dirs[: const.USER_ACCOUNT_MAX]
    skipped = account_dirs[const.USER_ACCOUNT_MAX :]
    for account in taken:
        shutil.copytree(account, new_config / account.name, dirs_exist_ok=True)
        _log(f'已迁移账户目录: config/{account.name}')
    if skipped:
        names = ', '.join(d.name for d in skipped)
        _log(f'账户超过 {const.USER_ACCOUNT_MAX} 个,未迁移: {names}')


def _copy_env_with_path_rewrite(src: Path, dest: Path, old_root: Path, new_root: Path) -> None:
    """复制 env.yml 并把旧项目根目录的绝对路径改写为新目录(正反斜杠都处理)。"""
    text = src.read_text(encoding='utf-8', errors='replace')
    replacements = {
        str(old_root): str(new_root),
        str(old_root).replace('\\', '/'): str(new_root).replace('\\', '/'),
        str(old_root).replace('\\', '\\\\'): str(new_root).replace('\\', '\\\\'),
    }
    for old, new in replacements.items():
        if old and old != new:
            text = text.replace(old, new)
    dest.write_text(text, encoding='utf-8')
    _log('env.yml 已迁移(其中的绝对路径已改写为新目录)')


def _copy_self_exe(new_root: Path) -> None:
    """把本工具 exe 拷进新目录,用户新目录自洽(不带旧日志)。"""
    if not getattr(sys, 'frozen', False):
        _log('源码运行模式,跳过拷贝本工具 exe')
        return
    try:
        dest = new_root / Path(sys.executable).name
        shutil.copy2(sys.executable, dest)
        _log(f'已拷贝本工具到新目录: {dest.name}')
    except Exception as exc:
        # exe 拷贝失败不致命:新目录仍可正常用启动器
        _log_error('拷贝本工具 exe 失败(不影响新目录使用)', exc)
