"""
系统信息检测器 - 协调器
协调新的硬件、系统、系统设置检测器，保持向后兼容
"""

import logging
from typing import Any, Dict

from oops.core.config import DetectionRule
from oops.detectors.hardware import HardwareDetector
from oops.detectors.system import SystemDetector
from oops.detectors.system_settings import SystemSettingsDetector

logger = logging.getLogger(__name__)


class SystemInfoDetector(DetectionRule):
    """系统信息检测器 - 作为协调器调用新的检测器"""

    def __init__(self):
        super().__init__(
            name="system_info",
            description="系统信息检测（协调器）",
            severity="info",
        )
        # 初始化子检测器
        self.hardware_detector = HardwareDetector()
        self.system_detector = SystemDetector()
        self.system_settings_detector = SystemSettingsDetector()

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统信息检测 - 协调多个子检测器"""
        try:
            # 调用各个子检测器
            hardware_result = self.hardware_detector.check(config)
            system_result = self.system_detector.check(config)
            settings_result = self.system_settings_detector.check(config)

            # 合并结果
            combined_details = {}
            
            # 添加硬件信息
            if hardware_result.get("status") == "success":
                hardware_details = hardware_result.get("details", {})
                combined_details.update({
                    "hardware": hardware_details.get("cpu", {}),
                    "memory": hardware_details.get("memory", {}),
                    "gpu": hardware_details.get("gpu"),
                    "storage": hardware_details.get("storage", {}),
                })

            # 添加系统信息
            if system_result.get("status") == "success":
                system_details = system_result.get("details", {})
                combined_details.update({
                    "basic": system_details.get("os", {}),
                    "python": system_details.get("python", {}),
                    "paths": system_details.get("paths", {}),
                })

            # 添加系统设置信息
            if settings_result.get("status") == "success":
                settings_details = settings_result.get("details", {})
                settings_data = settings_details.get("settings", {})
                if combined_details.get("basic"):
                    combined_details["basic"].update({
                        "hdr_enabled": settings_data.get("hdr_enabled", False),
                        "night_light_enabled": settings_data.get("night_light_enabled", False),
                        "color_filter_enabled": settings_data.get("color_filter_enabled", False),
                        "primary_resolution": settings_data.get("primary_resolution"),
                    })

            # 确定整体状态
            if settings_result.get("status") == "error":
                status = "warning"  # 系统设置错误降级为警告
                message = "系统信息收集完成，但发现系统设置问题"
            elif any(result.get("status") == "error" for result in [hardware_result, system_result]):
                status = "error"
                message = "系统信息收集部分失败"
            else:
                status = "success"
                message = "系统信息收集完成"

            return {
                "status": status,
                "message": message,
                "details": combined_details,
            }
        except Exception as e:
            logger.error(f"系统信息检测失败: {e}")
            return {"status": "error", "message": f"系统信息检测失败: {str(e)}"}

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        # 协调器模式：收集所有子检测器的修复建议
        suggestions = []
        
        # 从系统设置检测器获取建议
        if hasattr(self, 'system_settings_detector'):
            settings_result = result  # 这里可以进一步优化，分别获取各检测器结果
            settings_suggestion = self.system_settings_detector.get_fix_suggestion(settings_result)
            if settings_suggestion:
                suggestions.append(settings_suggestion)
        
        return "; ".join(filter(None, suggestions))
