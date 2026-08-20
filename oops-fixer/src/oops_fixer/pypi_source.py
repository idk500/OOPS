"""PyPI 源检测与自动切换。

兜底修复器不要求用户手动改配置。当前 pip_source 不可用时,自动写回可用源。
"""

from __future__ import annotations

import re
import shutil
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from oops_fixer.logging_utils import make_logger

ENV_CONFIG_RELATIVE_PATH: tuple[str, ...] = ('config', 'env.yml')
BACKUP_SUFFIX: str = '.oops-bak'
CHECK_PACKAGE: str = 'pip'
CHECK_TIMEOUT: float = 8.0

ALIBABA_SOURCE: str = 'https://mirrors.aliyun.com/pypi/simple'
PYPI_SOURCE: str = 'https://pypi.org/simple'
TSINGHUA_SOURCE: str = 'https://pypi.tuna.tsinghua.edu.cn/simple'

_SOURCE_LABELS: dict[str, str] = {
    ALIBABA_SOURCE: '阿里云',
    PYPI_SOURCE: '官方 PyPI',
    TSINGHUA_SOURCE: '清华大学',
}

_PIP_SOURCE_PATTERN: re.Pattern[str] = re.compile(r'^(\s*pip_source\s*:\s*)(.*?)(\s*)$')


@dataclass(frozen=True)
class SourceCheckResult:
    """单个 PyPI 源检测结果。"""

    url: str
    available: bool
    message: str


def ensure_available_pypi_source(project_root: Path) -> str | None:
    """检测并按需修复项目 pip_source。

    Args:
        project_root: 项目根目录

    Returns:
        最终使用的 pip_source;全部检测失败时返回 None
    """
    logger = make_logger()
    env_path = project_root.joinpath(*ENV_CONFIG_RELATIVE_PATH)
    current_source = _read_current_source(env_path)
    candidates = _build_candidates(current_source)

    if current_source:
        logger.info('当前 PyPI 源: %s', current_source)
    else:
        logger.info('未配置 PyPI 源,准备自动选择可用源')

    for source in candidates:
        result = _check_source(source)
        label = _SOURCE_LABELS.get(source, source)
        if result.available:
            logger.info('PyPI 源可用: %s (%s)', label, source)
            if source != current_source:
                _write_source(env_path, source)
                logger.info('已切换 PyPI 源为: %s (%s)', label, source)
            return source
        logger.warning('PyPI 源不可用: %s (%s) - %s', label, source, result.message)

    logger.error('所有 PyPI 源都不可用,保留原配置')
    return None


def _build_candidates(current_source: str | None) -> list[str]:
    """生成检测候选列表,不重复。"""
    raw_candidates = [current_source, ALIBABA_SOURCE, PYPI_SOURCE, TSINGHUA_SOURCE]
    candidates: list[str] = []
    seen: set[str] = set()
    for source in raw_candidates:
        if source is None:
            continue
        normalized = source.rstrip('/')
        if normalized in seen:
            continue
        seen.add(normalized)
        candidates.append(normalized)
    return candidates


def _read_current_source(env_path: Path) -> str | None:
    """读取 config/env.yml 中的 pip_source。"""
    if not env_path.is_file():
        return None
    try:
        for line in env_path.read_text(encoding='utf-8').splitlines():
            match = _PIP_SOURCE_PATTERN.match(line)
            if match is None:
                continue
            value = match.group(2).strip().strip('"').strip("'")
            return value.rstrip('/') if value else None
    except UnicodeDecodeError:
        for line in env_path.read_text(encoding='gbk', errors='ignore').splitlines():
            match = _PIP_SOURCE_PATTERN.match(line)
            if match is None:
                continue
            value = match.group(2).strip().strip('"').strip("'")
            return value.rstrip('/') if value else None
    return None


def _check_source(source: str) -> SourceCheckResult:
    """检测 PyPI simple 源是否可用。"""
    check_url = f'{source.rstrip("/")}/{CHECK_PACKAGE}/'
    request = urllib.request.Request(
        check_url,
        headers={'User-Agent': 'OneDragon-Oops/1.0'},
        method='GET',
    )
    try:
        with urllib.request.urlopen(request, timeout=CHECK_TIMEOUT) as response:
            status = getattr(response, 'status', 200)
            if status in {200, 301, 302, 403}:
                return SourceCheckResult(source, True, f'HTTP {status}')
            return SourceCheckResult(source, False, f'HTTP {status}')
    except urllib.error.HTTPError as exc:
        if exc.code in {200, 301, 302, 403}:
            return SourceCheckResult(source, True, f'HTTP {exc.code}')
        return SourceCheckResult(source, False, f'HTTP {exc.code}')
    except Exception as exc:
        return SourceCheckResult(source, False, str(exc))


def _write_source(env_path: Path, source: str) -> None:
    """写回 pip_source,保留其它配置。"""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if env_path.exists():
        backup_path = env_path.with_name(f'{env_path.name}{BACKUP_SUFFIX}')
        shutil.copy2(env_path, backup_path)
        lines = env_path.read_text(encoding='utf-8', errors='ignore').splitlines()
    else:
        lines = []

    replaced = False
    new_lines: list[str] = []
    for line in lines:
        match = _PIP_SOURCE_PATTERN.match(line)
        if match is None:
            new_lines.append(line)
            continue
        new_lines.append(f'{match.group(1)}{source}')
        replaced = True

    if not replaced:
        new_lines.append(f'pip_source: {source}')

    env_path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
