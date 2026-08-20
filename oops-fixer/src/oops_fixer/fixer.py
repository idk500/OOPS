"""急救流程编排:项目校验 → 进程清理 → git 急救 → 启动器更新

各步骤失败时:
  - 弹窗报错(MessageBoxW);
  - 日志已持久落盘(OneDragon-Oops.log);
  - 绝不闪退、绝不静默退出。
"""

from __future__ import annotations

import contextlib
import ctypes
import subprocess
from collections.abc import Callable
from pathlib import Path

from oops_fixer import const, detector, git_ops, launcher_updater, pypi_source, venv_doctor
from oops_fixer.logging_utils import make_logger


class Fixer:
    """兜底急救器主流程。"""

    def __init__(
        self,
        project_root: Path,
        on_log: Callable[[str], None],
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        """初始化。

        Args:
            project_root: 项目根目录
            on_log: 日志回调(UI 刷新用)
            on_finished: 全部流程结束后的回调(UI 负责收尾)
        """
        self.project_root: Path = project_root
        self.on_log: Callable[[str], None] = on_log
        self.on_finished: Callable[[], None] = on_finished
        self._logger = make_logger()

    def run(self) -> bool:
        """执行全部急救流程。

        Returns:
            True 表示全部步骤成功;False 表示中途失败(已弹窗并落盘日志)
        """
        try:
            self._run_steps()
        except Exception as exc:
            self._logger.error('急救流程出现未处理异常', exc_info=True)
            self._show_error(str(exc))
            return False
        else:
            return True
        finally:
            if self.on_finished is not None:
                with contextlib.suppress(Exception):
                    self.on_finished()

    # ---- 流程 ----

    def _run_steps(self) -> None:
        """按顺序执行急救步骤。"""
        self._log('==== 开始 OneDragon-Oops 兜底急救 ====')

        # 1. 结束占用本项目文件的进程,避免文件锁
        killed = detector.kill_project_processes(self.project_root)
        if killed:
            self._log(f'已结束 {len(killed)} 个占用本项目文件的进程')

        # 2. PyPI 源检测:当前源不可用时自动切换到可用源
        pypi_source.ensure_available_pypi_source(self.project_root)

        # 3. git 急救:强制切回主分支,丢弃一切改动
        git_ops.reset_repository_to_main(self.project_root)

        # 4. 虚拟环境体检:坏了/版本不符(不同版本启动器留下的遗留形态)就按启动器方式重建
        self._check_and_repair_venv()

        # 5. 启动器更新:按存在的 exe 文件名选形态,不是最新就从 CNB 拉最新替换
        picked = launcher_updater.pick_launcher(self.project_root)
        target_version = launcher_updater.resolve_target_version(self.project_root)
        if picked is None:
            self._log('未找到任何启动器(OneDragon-Launcher.exe / OneDragon-RuntimeLauncher.exe),跳过启动器更新')
        elif target_version is None:
            self._log('未能探测到最新版本,跳过启动器更新')
        else:
            exe_name, zip_name = picked
            self._log(f'启动器形态: {exe_name}')
            updated = launcher_updater.update_launcher(self.project_root, target_version, exe_name, zip_name)
            if not updated:
                self._log('启动器下载失败,跳过更新(代码已恢复,不影响使用)')

        self._log('==== 急救完成 ====')

    def _check_and_repair_venv(self) -> None:
        """体检并按需修复虚拟环境。

        - 正常:记录版本即可;
        - 缺失:项目带 uv 就顺手创建,没有就提示走启动器安装器(新克隆属正常现象,不算失败);
        - 损坏/版本不符:用项目自带 uv 按启动器的方式重建(先备份,失败回滚),失败则致命
          (下次双击进入完全重置,全量包自带可用环境)。
        """
        status, detail = venv_doctor.check_venv(self.project_root)
        self._log(f'虚拟环境体检: {detail}')

        if status == venv_doctor.STATUS_OK:
            return

        has_uv = (self.project_root / '.install' / 'uv' / 'uv.exe').is_file()
        if status == venv_doctor.STATUS_MISSING and not has_uv:
            self._log('虚拟环境缺失且项目未安装 uv,请先用启动器安装依赖(不算急救失败)')
            return

        self._log('开始重建虚拟环境(旧环境会自动备份)...')
        venv_doctor.repair_venv(self.project_root)

    # ---- 工具 ----

    def _log(self, message: str) -> None:
        """输出一行日志:同时给 UI 回调与日志文件。"""
        self._logger.info('%s', message)
        with contextlib.suppress(Exception):
            self.on_log(message)

    @staticmethod
    def _show_error(message: str) -> None:
        """弹窗报错(不阻塞太久,同时已落盘日志)。"""
        with contextlib.suppress(Exception):
            ctypes.windll.user32.MessageBoxW(
                None,
                f'急救失败:\n\n{message}\n\n详细日志见: OneDragon-Oops.log',
                'OneDragon-Oops 兜底修复器',
                0x10,  # MB_ICONERROR
            )

    def open_done_url(self) -> None:
        """急救完成后后台打开完整版 oops 工具页面。"""
        try:
            # 用 start 命令后台打开默认浏览器,避免 webbrowser 在 windowed exe 中卡住。
            subprocess.Popen(
                ['cmd', '/c', 'start', '', const.DONE_URL],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            self._logger.warning('打开完成页面失败: %s', const.DONE_URL)

    def open_launcher(self) -> None:
        """急救完成后打开启动器(按形态选择,目标缺失时回退另一种)。"""
        launcher_path = self._resolve_launcher_to_open()
        if launcher_path is None:
            self._logger.warning('两种启动器都不存在,跳过打开')
            return
        try:
            subprocess.Popen(
                ['cmd', '/c', 'start', '', str(launcher_path)],
                cwd=str(self.project_root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception:
            self._logger.warning('打开启动器失败: %s', launcher_path)

    def _resolve_launcher_to_open(self) -> Path | None:
        """按形态选启动器;选中的不存在时回退另一种(都无则 None)。"""
        picked = launcher_updater.pick_launcher(self.project_root)
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
        for name in candidates:
            path = self.project_root / name
            if path.is_file():
                return path
        return None
