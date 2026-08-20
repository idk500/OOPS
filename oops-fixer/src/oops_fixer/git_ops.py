"""git 急救:强制把本地代码切回主分支并丢弃一切改动

用 pygit2(libgit2)实现,不依赖系统 git,所以用户不装 git 也能用。
libgit2 在 Windows 上用系统 schannel 做 HTTPS 证书验证,不需要配置 CA。
"""

from __future__ import annotations

import contextlib
import re
import shutil
import time
from pathlib import Path

import pygit2
from pygit2 import (
    Oid,
    RemoteCallbacks,
    Repository,
    discover_repository,
    init_repository,
)
from pygit2.enums import ResetMode

from oops_fixer import const
from oops_fixer.logging_utils import make_logger

# 每次网络读写的空闲超时(秒):网络卡死时避免永远等下去
_IDLE_TIMEOUT: float = 120.0

# 版本标签形如 v2.5.1 / v2.5.1-beta.1
_VERSION_TAG_PATTERN: re.Pattern[str] = re.compile(r'^v\d+\.\d+\.\d+.*$')

def _log(message: str) -> None:
    """输出一行日志到文件(UI 由 logging 回调统一转发)。"""
    logger = make_logger()
    logger.info('%s', message)


def _log_error(message: str, exc: BaseException) -> None:
    """输出一行错误日志。"""
    logger = make_logger()
    logger.error('%s: %s', message, exc, exc_info=True)


class _TimeoutCallbacks(RemoteCallbacks):
    """给 fetch/list_heads 加超时,避免网络卡死卡住整个急救流程。"""

    def __init__(self, timeout: float) -> None:
        RemoteCallbacks.__init__(self)
        self._timeout: float = timeout
        self._started_at: float = time.monotonic()

    def _check(self) -> None:
        if time.monotonic() - self._started_at > self._timeout:
            raise TimeoutError(f'git 操作超过 {self._timeout:g} 秒')

    def transfer_progress(self, stats: object) -> None:
        self._check()

    def credentials(self, url: str, username_from_url: str | None, allowed_types: object) -> object:
        """公共仓库不需要用户名密码,若远端要求则匿名尝试。"""
        self._check()
        return pygit2.UserPass('x', 'x')

    def sideband_progress(self, data: str) -> None:
        self._check()


def reset_repository_to_main(project_root: Path) -> None:
    """强制把项目仓库切回主分支并丢弃一切本地改动。

    流程:
      1. 打开本地仓库(损坏则降级为重新 clone);
      2. 把所有 remote 删掉,只留 origin 指向 CNB;
      3. fetch origin/main + 所有 tags;
      4. 强制切到 main 并 hard reset 到 origin/main。

    Args:
        project_root: 项目根目录

    Raises:
        RuntimeError: 每一步失败都会抛出,由上层负责弹窗和落盘
    """
    git_dir = _find_git_dir(project_root)
    if git_dir is None:
        _log('本地没有可用的 .git 目录,走「重新拉取」路径')
        _clone_repository(project_root)
        return

    repo = _open_repo(git_dir)
    try:
        _force_remotes(repo)
        _fetch_origin(repo)
        _force_checkout_main(repo)
    except Exception as exc:
        _log_error('git 急救失败,尝试重新拉取', exc)
        _free_repo(repo)
        _clone_repository(project_root)
        return

    _free_repo(repo)
    _log('代码已强制切回主分支,并丢弃了所有本地改动')


def _find_git_dir(project_root: Path) -> Path | None:
    """在项目根目录下查找 .git 目录。"""
    discovered = discover_repository(str(project_root))
    if not discovered:
        return None
    git_dir = Path(discovered)
    if not git_dir.is_dir():
        return None
    return git_dir


def _open_repo(git_dir: Path) -> Repository:
    """打开仓库;打开失败时抛出,由上层降级重新拉取。"""
    try:
        return Repository(str(git_dir))
    except Exception as exc:
        raise RuntimeError(f'本地 git 仓库打不开: {git_dir}') from exc


def _free_repo(repo: Repository) -> None:
    """释放 pygit2 仓库句柄(避免 Windows 文件占用)。"""
    with contextlib.suppress(Exception):
        repo.free()


def _force_remotes(repo: Repository) -> None:
    """删掉所有 remote,只留 origin 指向 CNB。

    用户本地可能配了 github/cnb/upstream/myself 等一堆 remote,一键急救时全部清掉。
    """
    for name in list(repo.remotes.names()):
        if name == 'origin':
            continue
        try:
            repo.remotes.delete(name)
            _log(f'删除多余远程仓库: {name}')
        except Exception as exc:
            _log_error(f'删除远程仓库 {name} 失败', exc)

    if 'origin' not in repo.remotes.names():
        repo.remotes.create('origin', const.CNB_CLONE_URL)
        _log(f'创建远程仓库 origin -> {const.CNB_CLONE_URL}')
        return

    remote = repo.remotes['origin']
    if remote.url != const.CNB_CLONE_URL:
        repo.remotes.set_url('origin', const.CNB_CLONE_URL)
        _log(f'远程仓库 origin 地址改为 -> {const.CNB_CLONE_URL}')


def _fetch_origin(repo: Repository) -> None:
    """fetch origin 的 main 分支和所有 tags。"""
    _log('开始拉取最新代码(首次或长期未更新时数据量较大,请耐心等待)...')
    callbacks = _TimeoutCallbacks(const.GIT_OPERATION_TIMEOUT)
    remote = repo.remotes['origin']
    # + 强制更新本地 ref,避免本地分支指向旧提交时 fetch 拒绝
    remote.fetch(
        [f'+refs/heads/{const.PRIMARY_BRANCH}:refs/remotes/origin/{const.PRIMARY_BRANCH}',
         '+refs/tags/*:refs/tags/*'],
        callbacks=callbacks,
    )
    _log('拉取完成')


def _force_checkout_main(repo: Repository) -> None:
    """强制切到 main 并 hard reset 到 origin/main。"""
    remote_ref = f'refs/remotes/origin/{const.PRIMARY_BRANCH}'
    if remote_ref not in repo.references:
        raise RuntimeError(f'远程分支不存在: origin/{const.PRIMARY_BRANCH}')

    remote_oid: Oid = repo.references[remote_ref].target

    local_ref = f'refs/heads/{const.PRIMARY_BRANCH}'
    if local_ref not in repo.references:
        repo.create_branch(const.PRIMARY_BRANCH, repo.get(remote_oid))
        _log(f'创建本地分支 {const.PRIMARY_BRANCH}')

    # 直接 reset HARD 到远程提交,丢弃工作区与暂存区全部改动
    repo.reset(remote_oid, ResetMode.HARD)
    repo.set_head(local_ref)
    _log(f'强制切回主分支 {const.PRIMARY_BRANCH},已丢弃所有本地改动')


def _clone_repository(project_root: Path) -> None:
    """本地仓库缺失/损坏时:原地重建 .git 并 reset 到 CNB main。

    不能把整个项目目录改名,因为 OneDragon-Oops.exe 正在项目根目录运行,Windows 会占用自身。
    所以这里仅备份旧 .git,再在原目录初始化新仓库并拉取 main。
    """
    _log('重新建立本地 git 仓库,并拉取最新代码...')
    old_git = project_root / '.git'
    if old_git.exists():
        backup_git = project_root / f'.git.oops-bak-{time.strftime("%Y%m%d-%H%M%S")}'
        shutil.move(str(old_git), str(backup_git))
        _log(f'旧 .git 已备份: {backup_git.name}')

    repo = init_repository(str(project_root), initial_head=const.PRIMARY_BRANCH)
    try:
        repo.remotes.create('origin', const.CNB_CLONE_URL)
        _fetch_origin(repo)
        _force_checkout_main(repo)
    finally:
        _free_repo(repo)
    _log('本地 git 仓库重建完成')


def get_latest_tags() -> list[str]:
    """获取远程全部版本标签,按版本从新到旧排序。

    优先用本地仓库的 origin 探测;本地 .git 缺失/损坏(完全重置场景)时,
    退到临时 bare 仓探测,不依赖本地任何 git 状态。

    Returns:
        形如 ['v2.5.1', 'v2.5.0', ...] 的标签列表;失败时返回空列表
    """
    _log('正在探测最新版本...')
    callbacks = _TimeoutCallbacks(const.NETWORK_TIMEOUT)
    heads = _list_local_origin_heads(const.PROJECT_ROOT if const.PROJECT_ROOT else Path.cwd(), callbacks)
    if not heads:
        # 本地仓库打不开/没有 origin:用临时 bare 仓直接问 CNB
        import tempfile

        with tempfile.TemporaryDirectory(prefix='oops_tags_') as tmp:
            _log('本地仓库不可用,改用临时仓库探测远程版本...')
            try:
                bare = init_repository(tmp, bare=True)
                try:
                    bare.remotes.create('origin', const.CNB_CLONE_URL)
                    heads = _list_origin_heads(bare, callbacks)
                finally:
                    _free_repo(bare)
            except Exception as exc:
                _log_error('临时仓库探测版本失败', exc)
                return []

    tags = _extract_version_tags(heads)
    if not tags:
        _log_error('探测版本失败', RuntimeError('远程没有可用版本标签'))
    tags.sort(key=_version_key, reverse=True)
    return tags


def _list_origin_heads(repo: Repository, callbacks: _TimeoutCallbacks) -> list:
    """对给定仓库列出 origin 远端的全部引用,失败返回空列表。"""
    try:
        return list(repo.remotes['origin'].list_heads(callbacks=callbacks))
    except Exception as exc:
        _log_error('列远程引用失败', exc)
        return []


def _list_local_origin_heads(root: Path, callbacks: _TimeoutCallbacks) -> list:
    """打开本地仓库并列出 origin 引用;仓库不可用时返回空列表。"""
    try:
        repo = Repository(str(root))
    except Exception as exc:
        _log_error('打开本地仓库失败', exc)
        return []
    try:
        return _list_origin_heads(repo, callbacks)
    finally:
        _free_repo(repo)


def _extract_version_tags(heads: list) -> list[str]:
    """从远程引用列表里提取合法版本标签。"""
    tags: list[str] = []
    for head in heads:
        if head.name.startswith('refs/tags/'):
            tag = head.name[len('refs/tags/'):]
            if _VERSION_TAG_PATTERN.match(tag):
                tags.append(tag)
    return tags


def _version_key(tag: str) -> tuple[object, ...]:
    """版本标签排序键:按数字段比较,v2.10.0 比 v2.9.0 新。"""
    match = re.match(r'^v(\d+)\.(\d+)\.(\d+)', tag)
    if not match:
        return (0, 0, 0, tag)
    numbers = tuple(int(part) for part in match.groups())
    # 预发布版本(带 beta/rc)排在正式版后面
    is_prerelease = bool(re.search(r'(beta|rc|alpha)', tag, re.IGNORECASE))
    return (*numbers, 1 if not is_prerelease else 0, tag)
