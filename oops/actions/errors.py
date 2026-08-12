"""
错误处理:出错时把日志写入文件 + 弹置顶对话框(方便用户用手机拍照反馈)。

目标用户多半没有计算机基础,出错时只会用手机拍屏幕。因此:
  - 完整错误写入 oops-error.txt(与 exe 同目录)
  - 弹一个置顶的 tkinter 错误对话框,显示原因 + 日志路径,用户点确定才关闭
  - tkinter 不可用时回退到控制台 + 暂停
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ERROR_LOG_NAME = "oops-error.txt"


def error_log_path(install_dir: Path) -> Path:
    return install_dir / ERROR_LOG_NAME


def write_error_log(
    install_dir: Path, message: str, exc: Optional[BaseException] = None
) -> Path:
    """把错误详情写入 oops-error.txt(覆盖)。返回路径。"""
    path = error_log_path(install_dir)
    lines = [
        f"OOPS 出错时间: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "=== 错误信息 ===",
        message,
    ]
    if exc is not None:
        lines += [
            "",
            "=== 异常详情 ===",
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        ]
    try:
        path.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        logger.error("写错误日志失败: %s", e)
    return path


def show_error_dialog(message: str, log_path: Path) -> None:
    """置顶错误对话框;用户点确定才关。tkinter 不可用则回退控制台。"""
    text = (
        "OOPS 运行出错!\n\n"
        f"{message}\n\n"
        f"完整日志已保存到:\n{log_path}\n\n"
        "请用手机拍下本窗口,并把上面的 oops-error.txt 文件\n"
        "发给开发者,以便排查。"
    )
    # 优先 tkinter 置顶弹窗
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        messagebox.showerror("OOPS 出错了", text, parent=root)
        root.destroy()
        return
    except Exception as e:
        logger.error("tkinter 对话框不可用,回退控制台: %s", e)

    # 回退:控制台 + 暂停
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)
    try:
        input("\n按 Enter 键退出(或直接关闭窗口)...")
    except Exception:
        pass


def report_error(
    install_dir: Path, message: str, exc: Optional[BaseException] = None
) -> None:
    """记录日志 + 弹错误对话框。在顶层 except 中调用。"""
    log_path = write_error_log(install_dir, message, exc)
    logger.error("OOPS 出错: %s", message, exc_info=exc)
    show_error_dialog(message, log_path)
