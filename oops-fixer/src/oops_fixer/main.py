"""OneDragon-Oops 兜底修复器入口。"""

from __future__ import annotations

import ctypes
import sys
import time
from pathlib import Path

from oops_fixer import const, detector, full_reset
from oops_fixer.fixer import Fixer
from oops_fixer.logging_utils import (
    delete_log_file,
    init_logging,
    log_exception,
    make_logger,
    setup_fallback_handler,
    should_enter_reset_mode,
    write_result,
)
from oops_fixer.ui import FixerWindow


def _show_message(title: str, message: str, icon: int = 0x10) -> None:
    """显示 Windows 弹窗,失败时退回控制台输出。"""
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, icon)
    except Exception:
        print(f'{title}: {message}', file=sys.stderr)


def _get_runtime_dir() -> Path:
    """返回 exe 所在目录;源码运行时返回当前工作目录。"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path.cwd().resolve()


def _open_launcher_in(project_root: Path) -> None:
    """在指定目录打开启动器(按 .venv 形态选择,缺失时回退另一种)。"""
    import subprocess

    from oops_fixer import launcher_updater

    picked = launcher_updater.pick_launcher(project_root)
    if picked is not None:
        primary, _ = picked
        candidates = [
            primary,
            const.RUNTIME_LAUNCHER_EXE_NAME
            if primary == const.LAUNCHER_EXE_NAME
            else const.LAUNCHER_EXE_NAME,
        ]
    else:
        candidates = [const.LAUNCHER_EXE_NAME, const.RUNTIME_LAUNCHER_EXE_NAME]
    launcher_path = None
    for name in candidates:
        candidate = project_root / name
        if candidate.is_file():
            launcher_path = candidate
            break
    if launcher_path is None:
        make_logger().warning('新目录没有可用启动器,跳过打开')
        return
    subprocess.Popen(
        ['cmd', '/c', 'start', '', str(launcher_path)],
        cwd=str(project_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def main() -> int:
    """主入口。"""
    project_root = _get_runtime_dir()
    const.PROJECT_ROOT = project_root
    log_file = init_logging(project_root)
    logger = make_logger()
    logger.info('运行目录: %s', project_root)

    try:
        detector._validate_project_root(project_root)  # noqa: SLF001 - 急救入口需要先校验固定目录
    except Exception as exc:
        message = f'{exc}\n\n详细日志见:\n{log_file}'
        logger.error('项目根目录校验失败', exc_info=True)
        _show_message('OneDragon-Oops 兜底修复器', message, 0x10)
        # 让控制台运行时也能看到,双击 windowed 版不会显示控制台
        time.sleep(1)
        return 1

    # 结果协议:日志存在且末轮没有 RESULT: OK,说明上次急救失败 -> 本次直接完全重置
    reset_mode = should_enter_reset_mode()
    if reset_mode:
        logger.info('检测到上次急救失败(日志未清理),本次进入完全重置模式')

    if reset_mode:
        window = FixerWindow(
            const.COUNTDOWN_SECONDS,
            lambda: None,
            action_word='完全重置',
            status_text='上次急救失败,本次将下载完整环境包重建到新目录,请勿关闭窗口...',
        )
    else:
        window = FixerWindow(const.COUNTDOWN_SECONDS, lambda: None)
    setup_fallback_handler(window.append_log)

    def run_fixer() -> None:
        succeeded = False
        try:
            if reset_mode:
                new_root = full_reset.run_full_reset(project_root)
                window.append_log(f'已重建到新目录: {new_root}')
                _open_launcher_in(new_root)
                window.append_log('已从新目录打开 OneDragon-Launcher.exe')
                _show_message(
                    'OneDragon-Oops 完全重置完成',
                    '已重建到新目录:\n'
                    f'{new_root}\n\n'
                    '以后请在新目录运行;旧目录已保留,确认新目录正常后可手动删除。\n'
                    f'详细日志见: {log_file}',
                    0x40,  # MB_ICONINFORMATION
                )
            else:
                fixer = Fixer(project_root, lambda _: None)
                if fixer.run():
                    fixer.open_done_url()
                    window.append_log('已打开完整版 oops 工具页面')
                    fixer.open_launcher()
                    window.append_log('已打开 OneDragon-Launcher.exe')
                    succeeded = True
        except Exception as exc:
            log_exception(exc)
            _show_message(
                'OneDragon-Oops 兜底修复器',
                f'执行失败:\n\n{exc}\n\n详细日志见:\n{log_file}\n\n再次双击运行将进入完全重置模式。',
                0x10,
            )
        finally:
            # 结果协议:成功 -> 写 RESULT: OK 并删除整个日志(下次走正常急救);
            # 失败 -> 写 RESULT: FAILED 保留日志(下次启动进入完全重置)。
            if succeeded:
                write_result(True)
                delete_log_file()
                window.append_log('执行成功,日志已清理')
            else:
                write_result(False)
            window.append_log('流程结束,窗口将在 5 秒后关闭')
            window.root.after(5000, window.close)

    window.on_countdown_finished = run_fixer
    window.append_log(f'日志文件: {log_file}')
    if reset_mode:
        window.append_log('双击运行表示已同意完全重置,倒计时结束后自动执行。')
    else:
        window.append_log('双击运行表示已同意开始急救,5 秒倒计时结束后自动执行。')
    window.run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
