"""
系统信息检测器
检测操作系统、架构、Python环境等基本系统信息
"""

import logging
import os
import platform
import sys
from typing import Any, Dict

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class SystemDetector(DetectionRule):
    """系统信息检测器 - 收集操作系统和Python环境信息"""

    def __init__(self):
        super().__init__(
            name="system_info",
            description="系统信息检测",
            severity="info",
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统信息检测"""
        try:
            system_info = {
                "os": self._get_os_info(),
                "python": self._get_python_info(),
                "paths": self._get_path_info(),
            }

            return {
                "status": "success",
                "message": "系统信息收集完成",
                "details": system_info,
            }
        except Exception as e:
            logger.error(f"系统信息检测失败: {e}")
            return {"status": "error", "message": f"系统信息检测失败: {str(e)}"}

    def _get_os_info(self) -> Dict[str, Any]:
        """获取操作系统信息"""
        try:
            return {
                "name": platform.system(),
                "version": platform.version(),
                "release": platform.release(),
                "architecture": platform.architecture()[0],
                "machine": platform.machine(),
                "processor": platform.processor(),
            }
        except Exception as e:
            logger.error(f"获取操作系统信息失败: {e}")
            return {}

    def _get_python_info(self) -> Dict[str, Any]:
        """获取Python环境信息"""
        try:
            # 获取Python路径，但隐藏用户名部分
            python_exe = sys.executable
            username = os.getenv("USERNAME") or os.getenv("USER", "")
            if username:
                python_exe = python_exe.replace(username, "[USER]")

            return {
                "version": sys.version.split()[0],
                "executable": python_exe,
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler(),
            }
        except Exception as e:
            logger.error(f"获取Python信息失败: {e}")
            return {}

    def _get_path_info(self) -> Dict[str, Any]:
        """获取路径信息"""
        try:
            # 获取当前路径，但隐藏用户名部分
            current_path = os.getcwd()
            username = os.getenv("USERNAME") or os.getenv("USER", "")
            if username:
                current_path = current_path.replace(username, "[USER]")

            return {
                "current": current_path,
                "home": (
                    os.path.expanduser("~").replace(username, "[USER]")
                    if username
                    else os.path.expanduser("~")
                ),
            }
        except Exception as e:
            logger.error(f"获取路径信息失败: {e}")
            return {}

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议 - 系统信息不需要修复建议"""
        return ""
