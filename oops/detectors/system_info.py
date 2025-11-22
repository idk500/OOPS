"""
系统信息检测器
检测CPU、GPU、内存、存储等硬件信息
"""

import os
import platform
import sys
import psutil
import subprocess
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from oops.validators.path_validator import HardwareValidator

logger = logging.getLogger(__name__)


class SystemInfoDetector:
    """系统信息检测器"""
    
    def __init__(self):
        self.timeout = 10
        self.hardware_validator = HardwareValidator()
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统信息检测"""
        try:
            system_info = {
                'basic': self._get_basic_info(),
                'hardware': self._get_hardware_info(),
                'storage': self._get_storage_info()
            }
            
            # 验证硬件配置
            validation_results = self._validate_hardware(system_info)
            
            # 将验证结果添加到系统信息中
            system_info['validation'] = validation_results
            
            return {
                'status': 'success',
                'message': '系统信息收集完成',
                'details': system_info
            }
        except Exception as e:
            logger.error(f"系统信息检测失败: {e}")
            return {
                'status': 'error',
                'message': f'系统信息检测失败: {str(e)}'
            }
    
    def _validate_hardware(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证硬件配置"""
        from oops.validators.path_validator import PathValidator
        
        validation = {}
        
        # 验证内存
        hardware = system_info.get('hardware', {})
        memory_str = hardware.get('memory_total', '0 GB')
        try:
            memory_gb = float(memory_str.split()[0])
            validation['memory'] = self.hardware_validator.validate_memory(memory_gb)
        except:
            pass
        
        # 验证磁盘类型
        storage = system_info.get('storage', {})
        disk_type = storage.get('disk_type', 'Unknown')
        if disk_type != 'Unknown':
            validation['disk_type'] = self.hardware_validator.validate_disk_type(disk_type)
        
        # 验证用户名（不显示用户名本身，只显示验证结果）
        username = os.getenv('USERNAME') or os.getenv('USER', 'Unknown')
        path_validator = PathValidator()
        username_validation = path_validator.validate_username(username)
        
        # 只有在用户名有问题时才添加到验证结果中
        if not username_validation['valid'] or username_validation['warnings']:
            validation['username'] = {
                'valid': username_validation['valid'],
                'message': '用户名不符合规范' if not username_validation['valid'] else '用户名检测到潜在问题',
                'issues': username_validation['issues'],
                'warnings': username_validation['warnings'],
                'recommendations': username_validation['recommendations']
            }
        
        # 验证显示设置（HDR、夜间模式等）
        basic = system_info.get('basic', {})
        display_validation = self._validate_display_settings(basic)
        if display_validation:
            validation['display_settings'] = display_validation
        
        return validation
    
    def _validate_display_settings(self, basic_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """验证显示设置"""
        issues = []
        warnings = []
        recommendations = []
        
        # 检查 HDR
        hdr_enabled = basic_info.get('hdr_enabled')
        if hdr_enabled is True:
            issues.append('HDR已启用')
            recommendations.append('关闭HDR以避免影响游戏脚本的图像识别')
        
        # 检查夜间模式（Windows 护眼模式）
        night_light = basic_info.get('night_light_enabled')
        if night_light is True:
            warnings.append('夜间模式/护眼模式已启用')
            recommendations.append('关闭夜间模式以避免色温变化影响识别')
        
        # 检查颜色滤镜
        color_filter = basic_info.get('color_filter_enabled')
        if color_filter is True:
            issues.append('颜色滤镜已启用')
            recommendations.append('关闭颜色滤镜以避免颜色失真影响识别')
        
        # NVIDIA 游戏滤镜（如果检测到）
        nvidia_filter = basic_info.get('nvidia_filter_enabled')
        if nvidia_filter is True:
            warnings.append('可能启用了NVIDIA游戏滤镜')
            recommendations.append('如果使用了NVIDIA游戏滤镜，建议关闭以避免影响识别')
        
        # 检查显示器分辨率
        resolution = basic_info.get('primary_resolution')
        if resolution:
            resolution_valid = self._validate_resolution(resolution)
            if not resolution_valid['valid']:
                if resolution_valid['severity'] == 'error':
                    issues.append(f"主显示器分辨率过低: {resolution}")
                    recommendations.append('游戏脚本要求最低分辨率 1920x1080，请调整显示器分辨率')
                else:
                    warnings.append(f"显示器分辨率: {resolution}")
                    recommendations.append('建议使用 1920x1080 或更高分辨率以获得最佳识别效果')
        
        # 只有在有问题时才返回验证结果
        if issues or warnings:
            return {
                'valid': len(issues) == 0,
                'warning': len(warnings) > 0,
                'message': '检测到可能影响识别的显示设置' if issues else '检测到可能影响识别的显示设置（警告）',
                'issues': issues,
                'warnings': warnings,
                'recommendations': recommendations
            }
        
        return None
    
    def _get_basic_info(self) -> Dict[str, Any]:
        """获取基本系统信息"""
        try:
            # 获取Python路径，但隐藏用户名部分
            python_exe = sys.executable
            # 将用户名替换为 [USER]
            username = os.getenv('USERNAME') or os.getenv('USER', '')
            if username:
                python_exe = python_exe.replace(username, '[USER]')
            
            # 获取当前路径，但隐藏用户名部分
            current_path = os.getcwd()
            if username:
                current_path = current_path.replace(username, '[USER]')
            
            basic_info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'os_release': platform.release(),
                'architecture': platform.architecture()[0],
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': sys.version.split()[0],
                'python_executable': python_exe,
                'current_path': current_path
                # 注意：用户名和计算机名涉及隐私，已移除
            }
            
            # 检测显示设置（HDR等）
            display_settings = self._get_display_settings()
            if display_settings:
                basic_info.update(display_settings)
            
            return basic_info
        except Exception as e:
            logger.error(f"获取基本信息失败: {e}")
            return {}
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        hardware_info = {}
        
        try:
            # CPU信息
            hardware_info.update(self._get_cpu_info())
            
            # 内存信息
            hardware_info.update(self._get_memory_info())
            
            # GPU信息
            gpu_info = self._get_gpu_info()
            if gpu_info:
                hardware_info['gpu_info'] = gpu_info
                
        except Exception as e:
            logger.error(f"获取硬件信息失败: {e}")
        
        return hardware_info
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        try:
            cpu_info = {
                'cpu_cores_physical': psutil.cpu_count(logical=False),
                'cpu_cores_logical': psutil.cpu_count(logical=True),
            }
            
            # CPU频率
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info['cpu_freq_current'] = f"{cpu_freq.current:.0f} MHz"
                cpu_info['cpu_freq_max'] = f"{cpu_freq.max:.0f} MHz"
            
            # 尝试获取CPU型号
            cpu_model = self._get_cpu_model()
            if cpu_model:
                cpu_info['cpu_model'] = cpu_model
            
            return cpu_info
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {}
    
    def _get_cpu_model(self) -> Optional[str]:
        """获取CPU型号"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and line != 'Name':
                            return line
            elif platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':', 1)[1].strip()
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True,
                    text=True,
                    timeout=5
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
                'memory_total': f"{memory.total / (1024**3):.1f} GB",
                'memory_available': f"{memory.available / (1024**3):.1f} GB",
                'memory_used': f"{memory.used / (1024**3):.1f} GB",
                'memory_percent': f"{memory.percent:.1f}%"
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}
    
    def _get_gpu_info(self) -> Optional[str]:
        """获取GPU信息"""
        try:
            if platform.system() == "Windows":
                # 尝试使用wmic获取GPU信息
                result = subprocess.run(
                    ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    gpu_names = []
                    for line in lines:
                        line = line.strip()
                        if line and line != 'Name':
                            gpu_names.append(line)
                    return '; '.join(gpu_names) if gpu_names else None
            # 其他系统暂不支持
            return None
        except Exception as e:
            logger.debug(f"获取GPU信息失败: {e}")
            return None
    
    def _get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        storage_info = {}
        
        try:
            # 当前路径的磁盘信息
            current_path = Path.cwd()
            disk_usage = psutil.disk_usage(str(current_path))
            
            storage_info.update({
                'current_drive': str(current_path.anchor),
                'disk_total': f"{disk_usage.total / (1024**3):.1f} GB",
                'disk_used': f"{disk_usage.used / (1024**3):.1f} GB",
                'disk_free': f"{disk_usage.free / (1024**3):.1f} GB",
                'disk_usage_percent': f"{(disk_usage.used / disk_usage.total * 100):.1f}%"
            })
            
            # 检测磁盘类型
            disk_type = self._get_disk_type(current_path)
            if disk_type:
                storage_info['disk_type'] = disk_type
                
        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
        
        return storage_info
    
    def _get_disk_type(self, path: Path) -> Optional[str]:
        """检测磁盘类型（SSD/HDD）"""
        try:
            if platform.system() == "Windows":
                # 获取驱动器号
                drive = str(path.anchor).replace('\\', '')
                
                # 使用PowerShell检测磁盘类型
                ps_command = f"""
                Get-PhysicalDisk | Where-Object {{
                    $_.DeviceID -in (Get-Partition | Where-Object {{$_.DriveLetter -eq '{drive[0]}'}} | Get-Disk).Number
                }} | Select-Object -ExpandProperty MediaType
                """
                
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    media_type = result.stdout.strip()
                    if 'SSD' in media_type or 'Solid' in media_type:
                        return 'SSD'
                    elif 'HDD' in media_type or 'Hard' in media_type:
                        return 'HDD'
                    else:
                        return media_type if media_type else 'Unknown'
                        
            # Linux系统
            elif platform.system() == "Linux":
                # 尝试通过/sys/block检测
                try:
                    # 获取设备名
                    result = subprocess.run(
                        ['df', str(path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        device = result.stdout.split('\n')[1].split()[0]
                        device_name = device.split('/')[-1].rstrip('0123456789')
                        
                        # 检查rotational属性
                        rotational_path = f"/sys/block/{device_name}/queue/rotational"
                        if os.path.exists(rotational_path):
                            with open(rotational_path, 'r') as f:
                                rotational = f.read().strip()
                                return 'HDD' if rotational == '1' else 'SSD'
                except:
                    pass
                    
            return 'Unknown'
        except Exception as e:
            logger.debug(f"检测磁盘类型失败: {e}")
            return 'Unknown'
    
    def _get_display_settings(self) -> Dict[str, Any]:
        """获取显示设置（HDR、游戏滤镜、护眼模式、分辨率等）"""
        display_settings = {}
        
        try:
            if platform.system() == "Windows":
                # 检测 HDR 状态
                hdr_status = self._check_hdr_status()
                if hdr_status is not None:
                    display_settings['hdr_enabled'] = hdr_status
                
                # 检测夜间模式（Windows 护眼模式）
                night_light = self._check_night_light()
                if night_light is not None:
                    display_settings['night_light_enabled'] = night_light
                
                # 检测 NVIDIA 游戏滤镜
                nvidia_filter = self._check_nvidia_game_filter()
                if nvidia_filter is not None:
                    display_settings['nvidia_filter_enabled'] = nvidia_filter
                
                # 检测颜色滤镜
                color_filter = self._check_color_filter()
                if color_filter is not None:
                    display_settings['color_filter_enabled'] = color_filter
            
            # 检测显示器分辨率（跨平台）
            resolution = self._get_display_resolution()
            if resolution:
                display_settings['primary_resolution'] = resolution
                
        except Exception as e:
            logger.debug(f"获取显示设置失败: {e}")
        
        return display_settings
    
    def _check_hdr_status(self) -> Optional[bool]:
        """检测 Windows HDR 状态"""
        try:
            # 使用 PowerShell 检测 HDR 状态
            # Windows 10/11 的 HDR 设置存储在注册表中
            ps_command = """
            $hdrKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\VideoSettings'
            if (Test-Path $hdrKey) {
                $hdrValue = Get-ItemProperty -Path $hdrKey -Name 'EnableHDR' -ErrorAction SilentlyContinue
                if ($hdrValue) {
                    $hdrValue.EnableHDR
                } else {
                    0
                }
            } else {
                0
            }
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # 1 表示启用，0 表示禁用
                return output == '1'
            
            return None
        except Exception as e:
            logger.debug(f"检测 HDR 状态失败: {e}")
            return None
    
    def _check_night_light(self) -> Optional[bool]:
        """检测 Windows 夜间模式状态（护眼模式）"""
        try:
            ps_command = """
            $nightLightKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate'
            if (Test-Path $nightLightKey) {
                $value = Get-ItemProperty -Path $nightLightKey -Name 'Data' -ErrorAction SilentlyContinue
                if ($value) {
                    # Data 字段的第 18 个字节表示状态
                    $data = $value.Data
                    if ($data.Length -gt 18) {
                        $data[18] -eq 0x15
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
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                return output == 'true'
            
            return None
        except Exception as e:
            logger.debug(f"检测夜间模式失败: {e}")
            return None
    
    def _check_nvidia_game_filter(self) -> Optional[bool]:
        """检测 NVIDIA 游戏滤镜状态"""
        try:
            # NVIDIA 游戏滤镜通常通过 GeForce Experience 或驱动程序启用
            # 检查 NVIDIA 相关进程
            ps_command = """
            $nvidiaProcesses = Get-Process | Where-Object {$_.ProcessName -like '*NVIDIA*' -or $_.ProcessName -like '*GeForce*'}
            if ($nvidiaProcesses) {
                # 检查是否有游戏滤镜相关的进程
                $filterProcess = $nvidiaProcesses | Where-Object {$_.ProcessName -like '*Overlay*' -or $_.ProcessName -like '*Share*'}
                if ($filterProcess) {
                    $true
                } else {
                    $false
                }
            } else {
                $false
            }
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                # 注意：这只是检测进程，不能100%确定滤镜是否启用
                # 返回 None 表示无法确定
                return None
            
            return None
        except Exception as e:
            logger.debug(f"检测 NVIDIA 游戏滤镜失败: {e}")
            return None
    
    def _check_color_filter(self) -> Optional[bool]:
        """检测 Windows 颜色滤镜状态"""
        try:
            ps_command = """
            $colorFilterKey = 'HKCU:\\Software\\Microsoft\\ColorFiltering'
            if (Test-Path $colorFilterKey) {
                $value = Get-ItemProperty -Path $colorFilterKey -Name 'Active' -ErrorAction SilentlyContinue
                if ($value) {
                    $value.Active -eq 1
                } else {
                    $false
                }
            } else {
                $false
            }
            """
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                return output == 'true'
            
            return None
        except Exception as e:
            logger.debug(f"检测颜色滤镜失败: {e}")
            return None
    
    def _get_display_resolution(self) -> Optional[str]:
        """获取主显示器分辨率"""
        try:
            if platform.system() == "Windows":
                ps_command = """
                Add-Type -AssemblyName System.Windows.Forms
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen
                $width = $screen.Bounds.Width
                $height = $screen.Bounds.Height
                Write-Output "$width x $height"
                """
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    resolution = result.stdout.strip()
                    if 'x' in resolution:
                        return resolution
            elif platform.system() == "Linux":
                # 尝试使用 xrandr
                result = subprocess.run(
                    ['xrandr', '--query'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ' connected primary ' in line or ' connected ' in line:
                            # 查找分辨率信息
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and part.replace('x', '').replace('+', '').replace('-', '').isdigit():
                                    return part.split('+')[0]  # 去掉偏移量
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ['system_profiler', 'SPDisplaysDataType'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Resolution:' in line:
                            # 提取分辨率
                            resolution_part = line.split('Resolution:')[1].strip()
                            if 'x' in resolution_part:
                                return resolution_part.split()[0]  # 取第一个分辨率值
            return None
        except Exception as e:
            logger.debug(f"获取显示器分辨率失败: {e}")
            return None
    
    def _validate_resolution(self, resolution: str) -> Dict[str, Any]:
        """验证分辨率是否符合要求"""
        try:
            # 解析分辨率
            if 'x' in resolution:
                width_str, height_str = resolution.split('x', 1)
                width = int(width_str.strip())
                height = int(height_str.strip().split()[0])  # 去掉可能的额外信息
                
                # 最低要求：1920x1080
                min_width = 1920
                min_height = 1080
                
                if width < min_width or height < min_height:
                    return {
                        'valid': False,
                        'severity': 'error',
                        'message': f'分辨率 {width}x{height} 低于最低要求 {min_width}x{min_height}'
                    }
                elif width == min_width and height == min_height:
                    return {
                        'valid': True,
                        'severity': 'info',
                        'message': f'分辨率 {width}x{height} 符合最低要求'
                    }
                else:
                    return {
                        'valid': True,
                        'severity': 'info',
                        'message': f'分辨率 {width}x{height} 符合要求'
                    }
            else:
                return {
                    'valid': False,
                    'severity': 'warning',
                    'message': f'无法解析分辨率格式: {resolution}'
                }
        except (ValueError, IndexError) as e:
            return {
                'valid': False,
                'severity': 'warning',
                'message': f'分辨率解析失败: {resolution}'
            }
    
    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        suggestions = []
        
        validation = result.get('validation', {})
        
        # 内存建议
        if 'memory' in validation and not validation['memory'].get('valid'):
            suggestions.append(validation['memory'].get('recommendation', ''))
        
        # 磁盘类型建议
        if 'disk_type' in validation and validation['disk_type'].get('warning'):
            suggestions.append(validation['disk_type'].get('recommendation', ''))
        
        # 显示设置建议
        if 'display_settings' in validation and validation['display_settings'].get('warning'):
            suggestions.append(validation['display_settings'].get('recommendation', ''))
        
        # 如果没有建议，返回空字符串（不显示"无需修复"）
        return '; '.join(filter(None, suggestions))
