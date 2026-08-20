"""Tkinter 窗口:顶部 5 秒倒计时 + 日志区

双击运行后立即显示窗口,倒计时结束才开始真正动手。
用户看到窗口就代表「已同意开始急救」,所以倒计时期间不设任何按钮。
"""

from __future__ import annotations

import contextlib
import queue
import sys
import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import scrolledtext

from oops_fixer import const


class FixerWindow:
    """急救窗口:显示倒计时与执行日志。"""

    def __init__(
        self,
        countdown_seconds: int,
        on_countdown_finished: Callable[[], None],
        action_word: str = '急救',
        status_text: str = '即将开始急救,请勿关闭窗口...',
    ) -> None:
        """初始化窗口。

        Args:
            countdown_seconds: 倒计时秒数
            on_countdown_finished: 倒计时结束后的回调(在后台线程执行急救)
            action_word: 动作词(急救/完全重置),用于倒计时文案
            status_text: 倒计时期间的状态说明文字
        """
        self.countdown_seconds: int = countdown_seconds
        self.on_countdown_finished: Callable[[], None] = on_countdown_finished
        self.action_word: str = action_word

        self.root = tk.Tk()
        self.root.title('OneDragon-Oops 兜底修复器')
        self._set_window_icon()
        self.root.geometry('640x420')
        self.root.resizable(True, True)

        self._countdown_label = tk.Label(
            self.root,
            text='',
            font=('Microsoft YaHei', 20, 'bold'),
            fg='#c0392b',
        )
        self._countdown_label.pack(pady=(16, 4))

        self._status_label = tk.Label(
            self.root,
            text=status_text,
            font=('Microsoft YaHei', 10),
            fg='#555',
        )
        self._status_label.pack(pady=(0, 8))

        self._log_view = scrolledtext.ScrolledText(
            self.root,
            height=16,
            state='disabled',
            font=('Consolas', 9),
        )
        self._log_view.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        self._messages: queue.Queue[str] = queue.Queue()
        self._countdown_running = False

    def _set_window_icon(self) -> None:
        """设置窗口图标为 oops 图标。"""
        if getattr(sys, 'frozen', False):
            base_dir = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
        else:
            base_dir = Path.cwd()
        icon_path = base_dir.joinpath(*const.OOPS_ICON_RELATIVE_PATH)
        if icon_path.is_file():
            with contextlib.suppress(tk.TclError):
                self.root.iconbitmap(str(icon_path))

    # ---- 窗口生命周期 ----

    def run(self) -> None:
        """进入 Tk 主循环,并启动倒计时线程。"""
        self._countdown_running = True
        threading.Thread(target=self._run_countdown, daemon=True).start()
        self._poll_messages()
        self.root.mainloop()

    def close(self) -> None:
        """关闭窗口(急救完成后调用)。"""
        self._countdown_running = False
        self.root.after(0, self.root.destroy)

    # ---- 倒计时 ----

    def _run_countdown(self) -> None:
        """倒计时线程:每秒更新界面。"""
        remaining = self.countdown_seconds
        while remaining > 0 and self._countdown_running:
            self._update_countdown(remaining)
            if not self._wait(1.0):
                return
            remaining -= 1

        if not self._countdown_running:
            return

        self._update_countdown(0)
        self._wait(0.3)
        if self._countdown_running:
            self._set_status(f'开始{self.action_word}...')
            threading.Thread(target=self.on_countdown_finished, daemon=True).start()

    def _update_countdown(self, remaining: int) -> None:
        """更新倒计时文字。"""
        text = '开始倒计时...' if remaining <= 0 else f'{remaining} 秒后开始{self.action_word}'
        with contextlib.suppress(tk.TclError):
            self.root.after(0, lambda: self._countdown_label.configure(text=text))

    def _set_status(self, text: str) -> None:
        """更新状态文字。"""
        with contextlib.suppress(tk.TclError):
            self.root.after(0, lambda: self._status_label.configure(text=text))

    def _wait(self, seconds: float) -> bool:
        """等待指定秒数,窗口关闭时提前返回 False。"""
        import time
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if not self._countdown_running:
                return False
            time.sleep(0.05)
        return True

    # ---- 日志 ----

    def append_log(self, line: str) -> None:
        """把一行日志放进队列,由主线程刷新。"""
        self._messages.put(line)

    def _poll_messages(self) -> None:
        """主线程定期取出队列里的日志并刷新界面。"""
        try:
            while True:
                line = self._messages.get_nowait()
                self._log_view.configure(state='normal')
                self._log_view.insert('end', line + '\n')
                self._log_view.see('end')
                self._log_view.configure(state='disabled')
        except queue.Empty:
            pass
        self.root.after(50, self._poll_messages)
