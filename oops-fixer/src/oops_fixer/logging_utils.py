"""日志工具:一份日志同时写入日志文件和窗口回调

兜底修复器要求「弹窗 + 持久记录」,不能闪退,日志文件用来给用户远程排查。
"""

from __future__ import annotations

import contextlib
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from oops_fixer import const

_LOG_FILE: Path | None = None
_LOG_HANDLER: logging.FileHandler | None = None


def init_logging(log_dir: Path | None = None) -> Path:
    """初始化日志文件输出,返回日志文件路径。

    Args:
        log_dir: 日志目录;None 时使用项目根目录

    Returns:
        日志文件完整路径
    """
    global _LOG_FILE, _LOG_HANDLER
    root_dir = log_dir or (const.PROJECT_ROOT or Path.cwd())
    log_file = root_dir / const.LOG_FILE_NAME

    logger = logging.getLogger('oops_fixer')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if _LOG_HANDLER is not None:
        logger.removeHandler(_LOG_HANDLER)
        _LOG_HANDLER.close()

    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    _LOG_HANDLER = handler
    _LOG_FILE = log_file

    logger.info(const.RUN_BANNER)
    return log_file


def get_log_file() -> Path | None:
    """返回当前日志文件路径(未初始化时返回 None)。"""
    return _LOG_FILE


def make_logger() -> logging.Logger:
    """返回带文件输出的 logger 实例。"""
    logger = logging.getLogger('oops_fixer')
    if _LOG_FILE is None:
        init_logging()
    return logger


def setup_fallback_handler(on_log: Callable[[str], None]) -> logging.Handler:
    """注册一个把日志同时转发给 UI 回调的 handler。

    Args:
        on_log: 接收单行日志文本的回调(UI 用来刷新窗口内容)

    Returns:
        创建的 handler(调用方可自行 removeHandler)
    """
    class _CallbackHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            message = self.format(record)
            with contextlib.suppress(Exception):
                on_log(message)

    handler = _CallbackHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger('oops_fixer')
    logger.addHandler(handler)
    return handler


def log_exception(exc: BaseException) -> None:
    """把异常输出到日志并打印到 stderr(便于双击运行时看到)。"""
    logger = make_logger()
    logger.error('发生异常: %s', exc, exc_info=True)
    with contextlib.suppress(Exception):
        print(f'[oops_fixer] {type(exc).__name__}: {exc}', file=sys.stderr)


def write_result(ok: bool) -> None:
    """在日志末尾写一行运行结果(结果协议)。

    成功后整个日志会被 delete_log_file() 删除;失败时保留日志,
    下次启动检测到「末轮无 RESULT: OK」即进入完全重置模式。
    """
    logger = make_logger()
    logger.info(const.RESULT_OK_LINE if ok else const.RESULT_FAILED_LINE)


def delete_log_file() -> None:
    """删除日志文件并关闭句柄(仅在整轮成功后调用)。"""
    global _LOG_FILE, _LOG_HANDLER
    logger = logging.getLogger('oops_fixer')
    if _LOG_HANDLER is not None:
        with contextlib.suppress(Exception):
            logger.removeHandler(_LOG_HANDLER)
        with contextlib.suppress(Exception):
            _LOG_HANDLER.close()
        _LOG_HANDLER = None
    if _LOG_FILE is not None:
        with contextlib.suppress(OSError):
            _LOG_FILE.unlink(missing_ok=True)
        _LOG_FILE = None


def should_enter_reset_mode() -> bool:
    """根据日志判断下次(本次)启动是否进入完全重置模式。

    规则:日志文件存在,且其中最后一次「protocol-v2 启动横幅」之后没有 RESULT: OK。
    - 没有横幅(旧版工具留下的日志/无日志)→ 不触发,走正常急救;
    - 横幅后是 RESULT: FAILED 或没有任何结果行(硬崩溃)→ 触发重置。
    """
    if _LOG_FILE is None or not _LOG_FILE.is_file():
        return False
    try:
        text = _LOG_FILE.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return False

    lines = text.splitlines()
    banner_at = -1
    for index, line in enumerate(lines):
        if const.RUN_BANNER in line:
            banner_at = index
    if banner_at < 0:
        return False  # 旧格式日志:不触发,避免升级用户误重置
    last_result: str | None = None
    for line in lines[banner_at + 1 :]:
        if const.RESULT_OK_LINE in line:
            last_result = const.RESULT_OK_LINE
        elif const.RESULT_FAILED_LINE in line:
            last_result = const.RESULT_FAILED_LINE
    return last_result != const.RESULT_OK_LINE
