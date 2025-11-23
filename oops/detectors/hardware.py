"""
硬件信息检测器
检测CPU、GPU、内存、存储等硬件信息
"""

import logging
import platform
import subprocess
from typing import Any, Dict, Optional

import psutil

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class HardwareDetector(DetectionRule):
    """硬件信息检测器 - 收集数据并进行硬件要求验证"""

    def __init__(self):
        super().__init__(
            name="hardware_info",
            description="硬件信息检测",
            severity="info",
        )
        self.timeout = 10

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行硬件信息检测"""
        try:
            hardware_info = {
                "cpu": self._get_cpu_info(),
                "memory": self._get_memory_info(),
                "gpu": self._get_gpu_info(),
                "storage": self._get_storage_info(),
                "display": self._get_display_info(),
            }
            
            # 进行硬件要求验证
            issues = []
            warnings = []
            
            # 验证分辨率（从项目配置中获取最低要求）
            min_resolution = config.get("hardware_requirements", {}).get("min_resolution", "1920x1080")
            display_info = hardware_info.get("display", {})
            current_resolution = display_info.get("primary_resolution", "")
            
            if current_resolution and min_resolution:
                if not self._check_resolution_requirement(current_resolution, min_resolution):
                    issues.append(f"主显示器分辨率 {current_resolution} 低于最低要求 {min_resolution}")
            
            # 确定状态
            if issues:
                status = "error"
                message = f"硬件检测完成，发现 {len(issues)} 个不符合要求的项"
                severity = "error"
            elif warnings:
                status = "warning"
                message = f"硬件检测完成，发现 {len(warnings)} 个警告"
                severity = "warning"
            else:
                status = "success"
                message = "硬件检测完成，所有硬件符合要求"
                severity = "info"
            
            # 更新severity
            self.severity = severity
            
            return {
                "status": status,
                "message": message,
                "details": {
                    **hardware_info,
                    "issues": issues,
                    "warnings": warnings,
                },
            }
        except Exception as e:
            logger.error(f"硬件信息检测失败: {e}")
            return {"status": "error", "message": f"硬件信息检测失败: {str(e)}"}

    def _get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        try:
            cpu_info = {
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
            }

            # CPU频率
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info["freq_current"] = f"{cpu_freq.current:.0f} MHz"
                cpu_info["freq_max"] = f"{cpu_freq.max:.0f} MHz"

            # CPU型号
            cpu_model = self._get_cpu_model()
            if cpu_model:
                cpu_info["model"] = cpu_model

            return cpu_info
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {}

    def _get_cpu_model(self) -> Optional[str]:
        """获取CPU型号"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and line != "Name":
                            return line
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name"):
                            return line.split(":", 1)[1].strip()
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logger.debug(f"获取CPU型号失败: {e}")
        return None

    def _get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": f"{memory.total / (1024**3):.1f} GB",
                "available": f"{memory.available / (1024**3):.1f} GB",
                "used": f"{memory.used / (1024**3):.1f} GB",
                "percent": f"{memory.percent:.1f}%",
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}

    def _get_gpu_info(self) -> Optional[str]:
        """获取GPU信息"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    gpus = []
                    for line in lines:
                        line = line.strip()
                        if line and line != "Name":
                            gpus.append(line)
                    return ", ".join(gpus) if gpus else None
        except Exception as e:
            logger.debug(f"获取GPU信息失败: {e}")
        return None

    def _get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        try:
            import os

            # 获取当前驱动器
            current_drive = os.path.splitdrive(os.getcwd())[0] + os.sep

            # 获取磁盘使用情况
            disk_usage = psutil.disk_usage(current_drive)

            storage_info = {
                "current_drive": current_drive,
                "total": f"{disk_usage.total / (1024**3):.1f} GB",
                "used": f"{disk_usage.used / (1024**3):.1f} GB",
                "free": f"{disk_usage.free / (1024**3):.1f} GB",
                "percent": f"{disk_usage.percent:.1f}%",
            }

            # 检测磁盘类型
            disk_type = self._get_disk_type(current_drive)
            if disk_type:
                storage_info["type"] = disk_type

            return storage_info
        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
            return {}

    def _get_disk_type(self, drive: str) -> Optional[str]:
        """检测磁盘类型（SSD/HDD）"""
        try:
            if platform.system() == "Windows":
                # 使用 PowerShell 检测磁盘类型
                drive_letter = drive.rstrip(":\\")
                ps_command = f"""
                $partition = Get-Partition -DriveLetter {drive_letter} -ErrorAction SilentlyContinue
                if ($partition) {{
                    $disk = Get-PhysicalDisk -DeviceNumber $partition.DiskNumber -ErrorAction SilentlyContinue
                    if ($disk) {{
                        $disk.MediaType
                    }}
                }}
                """
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if result.returncode == 0:
                    media_type = result.stdout.strip()
                    if "SSD" in media_type or "Solid" in media_type:
                        return "SSD"
                    elif "HDD" in media_type or "Hard" in media_type:
                        return "HDD"
        except Exception as e:
            logger.debug(f"检测磁盘类型失败: {e}")
        return "Unknown"

    def _get_display_info(self) -> Dict[str, Any]:
        """获取显示器信息"""
        try:
            if platform.system() == "Windows":
                # 使用 PowerShell 获取主显示器分辨率
                ps_command = """
                Add-Type -AssemblyName System.Windows.Forms
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                $width = $screen.Bounds.Width
                $height = $screen.Bounds.Height
                Write-Output "$width x $height"
                """
                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                if result.returncode == 0:
                    resolution = result.stdout.strip()
                    return {"primary_resolution": resolution}
        except Exception as e:
            logger.debug(f"获取显示器信息失败: {e}")
        return {}
    
    def _check_resolution_requirement(self, current: str, required: str) -> bool:
        """检查分辨率是否满足要求"""
        try:
            # 解析当前分辨率
            current_parts = current.replace(" ", "").split("x")
            if len(current_parts) != 2:
                return True  # 无法解析，跳过检查
            current_width = int(current_parts[0])
            current_height = int(current_parts[1])
            
            # 解析要求分辨率
            required_parts = required.replace(" ", "").split("x")
            if len(required_parts) != 2:
                return True  # 无法解析，跳过检查
            required_width = int(required_parts[0])
            required_height = int(required_parts[1])
            
            # 检查是否满足要求
            return current_width >= required_width and current_height >= required_height
        except Exception as e:
            logger.debug(f"检查分辨率要求失败: {e}")
            return True  # 出错时跳过检查

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        details = result.get("details", {})
        issues = details.get("issues", [])
        
        if issues:
            suggestions = []
            for issue in issues:
                if "分辨率" in issue:
                    suggestions.append("请调整显示器分辨率以满足游戏要求")
            return "; ".join(suggestions) if suggestions else ""
        return ""
