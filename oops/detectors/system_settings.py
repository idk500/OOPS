"""
系统设置检测器
检测显示设置（HDR、夜间模式、分辨率等）和其他可能影响游戏脚本的系统设置
"""

import logging
import platform
import subprocess
from typing import Any, Dict, List, Optional

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class SystemSettingsDetector(DetectionRule):
    """系统设置检测器 - 检测可能影响游戏脚本的系统设置"""

    def __init__(self):
        super().__init__(
            name="system_settings",
            description="系统设置检测",
            severity="warning",
        )
        self.timeout = 10

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统设置检测"""
        try:
            settings = self._get_display_settings()
            
            # 获取系统设置配置
            system_settings_config = config.get("checks", {}).get("system_settings", {})

            # 分析设置问题
            issues = []
            warnings = []
            recommendations = []

            # 检查管理员权限
            require_admin = system_settings_config.get("require_admin", False)
            is_admin = settings.get("is_admin")
            
            if require_admin and is_admin is False:
                issues.append("未以管理员权限运行")
                recommendations.append("请右键点击程序，选择「以管理员身份运行」")
            
            # 检查 HDR
            if settings.get("hdr_enabled") is True:
                issues.append("HDR已启用")
                recommendations.append("关闭HDR以避免影响游戏脚本的图像识别")

            # 检查夜间模式
            if settings.get("night_light_enabled") is True:
                warnings.append("夜间模式/护眼模式已启用")
                recommendations.append("关闭夜间模式以避免色温变化影响识别")

            # 检查颜色滤镜
            if settings.get("color_filter_enabled") is True:
                issues.append("颜色滤镜已启用")
                recommendations.append("关闭颜色滤镜以避免颜色失真影响识别")

            # 检查分辨率
            resolution = settings.get("primary_resolution")
            if resolution:
                resolution_check = self._validate_resolution(resolution)
                if not resolution_check["valid"]:
                    if resolution_check["severity"] == "error":
                        issues.append(f"主显示器分辨率过低: {resolution}")
                        recommendations.append(
                            "游戏脚本要求最低分辨率 1920x1080，请调整显示器分辨率"
                        )
                    else:
                        warnings.append(f"显示器分辨率: {resolution}")
                        recommendations.append(
                            "建议使用 1920x1080 或更高分辨率以获得最佳识别效果"
                        )

            # 获取游戏内设置提醒
            game_settings_reminder = system_settings_config.get("game_settings_reminder", [])
            
            # 确定状态
            if issues:
                status = "error"
                message = f"检测到 {len(issues)} 个可能影响识别的系统设置问题"
            elif warnings:
                status = "warning"
                message = f"检测到 {len(warnings)} 个可能影响识别的系统设置警告"
            else:
                status = "success"
                message = "系统设置检查通过"

            details = {
                "settings": settings,
                "issues": issues,
                "warnings": warnings,
                "recommendations": recommendations,
            }
            
            # 如果有游戏内设置提醒，添加到详情中
            if game_settings_reminder:
                details["game_settings_reminder"] = game_settings_reminder

            return {
                "status": status,
                "message": message,
                "details": details,
            }
        except Exception as e:
            logger.error(f"系统设置检测失败: {e}")
            return {"status": "error", "message": f"系统设置检测失败: {str(e)}"}

    def _get_display_settings(self) -> Dict[str, Any]:
        """获取显示设置"""
        settings = {}

        try:
            if platform.system() == "Windows":
                # 检测管理员权限（不触发 UAC）
                settings["is_admin"] = self._check_admin_windows()
                
                # 检测 HDR
                settings["hdr_enabled"] = self._check_hdr_windows()

                # 检测夜间模式
                settings["night_light_enabled"] = self._check_night_light_windows()

                # 检测颜色滤镜
                settings["color_filter_enabled"] = self._check_color_filter_windows()

                # 获取主显示器分辨率
                settings["primary_resolution"] = self._get_primary_resolution_windows()

        except Exception as e:
            logger.debug(f"获取显示设置失败: {e}")

        return settings
    
    def _check_admin_windows(self) -> Optional[bool]:
        """检测是否以管理员权限运行（不触发 UAC）"""
        try:
            import ctypes
            # 使用 shell32.IsUserAnAdmin() 检查当前进程是否有管理员权限
            # 这个方法不会触发 UAC，只是检查当前进程的权限状态
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.debug(f"检测管理员权限失败: {e}")
            return None

    def _check_hdr_windows(self) -> Optional[bool]:
        """检测Windows HDR状态"""
        try:
            # 正确的HDR检测方法：读取注册表
            ps_command = """
            $hdrKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\VideoSettings'
            if (Test-Path $hdrKey) {
                $hdrValue = Get-ItemProperty -Path $hdrKey -Name 'EnableHDR' -ErrorAction SilentlyContinue
                if ($hdrValue -and $hdrValue.EnableHDR -eq 1) {
                    $true
                } else {
                    $false
                }
            } else {
                $false
            }
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                return "True" in result.stdout
        except Exception as e:
            logger.debug(f"检测HDR失败: {e}")
        return None

    def _check_night_light_windows(self) -> Optional[bool]:
        """检测Windows夜间模式状态"""
        try:
            # 正确的夜间模式检测：检查Data字段的第18个字节
            ps_command = """
            $path = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate'
            if (Test-Path $path) {
                $value = Get-ItemProperty -Path $path -Name Data -ErrorAction SilentlyContinue
                if ($value -and $value.Data -and $value.Data.Length -gt 18) {
                    # 第18个字节为0x15表示启用，0x13表示禁用
                    if ($value.Data[18] -eq 0x15) {
                        $true
                    } else {
                        $false
                    }
                } else {
                    $false
                }
            } else {
                $false
            }
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                return "True" in result.stdout
        except Exception as e:
            logger.debug(f"检测夜间模式失败: {e}")
        return None

    def _check_color_filter_windows(self) -> Optional[bool]:
        """检测Windows颜色滤镜状态"""
        try:
            ps_command = """
            $path = 'HKCU:\\Software\\Microsoft\\ColorFiltering'
            if (Test-Path $path) {
                $value = Get-ItemProperty -Path $path -Name Active -ErrorAction SilentlyContinue
                if ($value.Active -eq 1) { $true } else { $false }
            } else { $false }
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                return "True" in result.stdout
        except Exception as e:
            logger.debug(f"检测颜色滤镜失败: {e}")
        return None

    def _get_primary_resolution_windows(self) -> Optional[str]:
        """获取Windows主显示器分辨率"""
        try:
            ps_command = """
            Add-Type -AssemblyName System.Windows.Forms
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen
            "$($screen.Bounds.Width) x $($screen.Bounds.Height)"
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"获取分辨率失败: {e}")
        return None

    def _validate_resolution(self, resolution: str) -> Dict[str, Any]:
        """验证分辨率是否符合要求"""
        try:
            # 解析分辨率字符串 "1920 x 1080"
            parts = resolution.split("x")
            if len(parts) == 2:
                width = int(parts[0].strip())
                height = int(parts[1].strip())

                # 最低要求 1920x1080
                if width < 1920 or height < 1080:
                    return {
                        "valid": False,
                        "severity": "error",
                        "message": f"分辨率过低: {resolution}",
                    }
                # 推荐 1920x1080 或更高
                elif width < 1920 or height < 1080:
                    return {
                        "valid": False,
                        "severity": "warning",
                        "message": f"分辨率偏低: {resolution}",
                    }
                else:
                    return {"valid": True, "message": f"分辨率正常: {resolution}"}
        except Exception as e:
            logger.debug(f"验证分辨率失败: {e}")

        return {"valid": True, "message": "无法验证分辨率"}

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        details = result.get("details", {})
        recommendations = details.get("recommendations", [])
        return "; ".join(recommendations) if recommendations else ""
