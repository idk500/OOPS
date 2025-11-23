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
    """硬件信息检测器 - 只收集数据，不做验证"""

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
            }

            return {
                "status": "success",
                "message": "硬件信息收集完成",
                "details": hardware_info,
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

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议 - 硬件信息不需要修复建议"""
        return ""
