"""
oops boot 的 GUI 引导窗

双击 oops.exe 时用这个:进度/倒数/错误都显示在一个**置顶 tkinter 窗口**里,
不依赖(且隐藏)黑控制台。出错时窗口保留,方便用户用手机拍照反馈。

boot 逻辑在独立线程中跑,通过队列把状态发回主线程(GUI)。
"""

import ctypes
import queue
import threading
import tkinter as tk
from pathlib import Path
from typing import Tuple


def hide_console() -> None:
    """Windows: 隐藏当前控制台窗口(双击时不闪黑框)。非 Windows/无控制台则空操作。"""
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
    except Exception:
        pass


def run_boot_window(path: str, install_dir: Path) -> int:
    """以置顶 GUI 窗运行 boot;成功关窗、失败在窗内显示错误(可截图)。返回退出码。"""
    from oops.actions.errors import write_error_log

    root = tk.Tk()
    root.title("OOPS - 一条龙启动器")
    root.geometry("580x340")
    root.minsize(420, 240)
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass
    root.configure(padx=18, pady=14)

    status = tk.StringVar(value="正在准备…")
    title_lbl = tk.Label(
        root,
        textvariable=status,
        font=("Microsoft YaHei", 13, "bold"),
        wraplength=540,
        justify="left",
    )
    title_lbl.pack(anchor="w")

    log = tk.Text(
        root,
        height=12,
        wrap="word",
        font=("Consolas", 10),
        bg="#f5f5f5",
        relief="flat",
    )
    log.pack(fill="both", expand=True, pady=(10, 0))

    q: "queue.Queue[Tuple[str, object]]" = queue.Queue()

    def worker() -> None:
        from oops.actions.boot import boot

        try:
            boot(path, reporter=lambda m: q.put(("msg", m)))
            q.put(("done", None))
        except Exception as e:
            q.put(("error", e))

    threading.Thread(target=worker, daemon=True).start()

    state = {"finished": False}

    def poll() -> None:
        if state["finished"]:
            return
        try:
            while True:
                kind, payload = q.get_nowait()
                if kind == "msg":
                    status.set(str(payload))
                    log.insert("end", str(payload) + "\n")
                    log.see("end")
                elif kind == "done":
                    status.set("已完成,正在启动一条龙。")
                    state["finished"] = True
                    root.after(400, root.destroy)
                    return
                elif kind == "error":
                    _show_error_state(root, status, log, payload, install_dir)
                    state["finished"] = True
                    return
        except queue.Empty:
            pass
        root.after(120, poll)

    poll()
    root.mainloop()
    return 0


def _show_error_state(
    root: tk.Tk,
    status: tk.StringVar,
    log: tk.Text,
    exc: BaseException,
    install_dir: Path,
) -> None:
    """在窗口内显示错误并保留,写 oops-error.txt。"""
    from oops.actions.errors import write_error_log

    msg = str(exc)
    log_path = write_error_log(install_dir, f"启动一条龙时出错:\n{msg}", exc)
    status.set("出错了 — 请用手机拍下本窗口")
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass
    log.insert("end", "\n" + "=" * 40 + "\n")
    log.insert("end", f"出错: {msg}\n\n")
    log.insert("end", f"完整日志已保存到:\n{log_path}\n\n")
    log.insert("end", "请拍下本窗口,并把上面的 oops-error.txt 发给开发者。\n")
    log.see("end")

    tk.Button(root, text="我已截图,关闭", command=root.destroy).pack(pady=(8, 0))
