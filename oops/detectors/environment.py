"""
环境依赖检测器
检测Python环境、系统运行库、虚拟环境等依赖项
"""

import sys
import subprocess
import platform
import os
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class EnvironmentDependencyDetector(DetectionRule):
    """环境依赖检测器"""
    
    def __init__(self):
        super().__init__(
            name="environment_dependencies",
            description="检测环境依赖",
            severity="error"
        )
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行环境依赖检测"""
        env_config = config.get('checks', {}).get('environment', {})
        if not env_config.get('enabled', False):
            return {
                'status': 'skipped',
                'message': '环境检测已禁用'
            }
        
        results = {}
        
        # Python版本检测
        python_version_check = self._check_python_version(env_config)
        results['python_version'] = python_version_check
        
        # 虚拟环境检测
        virtual_env_check = self._check_virtual_environment(env_config)
        results['virtual_environment'] = virtual_env_check
        
        # 系统运行库检测
        system_libraries_check = self._check_system_libraries(env_config)
        results['system_libraries'] = system_libraries_check
        
        # 项目特定依赖检测
        project_deps_check = self._check_project_dependencies(config)
        results['project_dependencies'] = project_deps_check
        
        # 分析整体环境状态
        overall_status = self._analyze_environment_status(results)
        
        return {
            'status': overall_status,
            'message': f'环境检测完成，共执行 {len(results)} 项检查',
            'details': results
        }
    
    def _check_python_version(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测Python版本兼容性"""
        try:
            current_version = sys.version_info
            required_version = env_config.get('python_version', '>=3.8')
            
            # 解析版本要求
            if required_version.startswith('>='):
                min_version = tuple(map(int, required_version[2:].split('.')))
                is_compatible = current_version >= min_version
            elif required_version.startswith('=='):
                exact_version = tuple(map(int, required_version[2:].split('.')))
                is_compatible = current_version[:2] == exact_version[:2]  # 只比较主次版本
            else:
                # 默认要求 >= 3.8
                is_compatible = current_version >= (3, 8)
            
            if is_compatible:
                return {
                    'status': 'success',
                    'current_version': f"{current_version.major}.{current_version.minor}.{current_version.micro}",
                    'required_version': required_version,
                    'message': f'Python版本兼容: {current_version.major}.{current_version.minor}.{current_version.micro}'
                }
            else:
                return {
                    'status': 'error',
                    'current_version': f"{current_version.major}.{current_version.minor}.{current_version.micro}",
                    'required_version': required_version,
                    'message': f'Python版本不兼容: 当前 {current_version.major}.{current_version.minor}.{current_version.micro}, 需要 {required_version}'
                }
                
        except Exception as e:
            logger.error(f"Python版本检测失败: {e}")
            return {
                'status': 'error',
                'message': f'Python版本检测失败: {str(e)}'
            }
    
    def _check_virtual_environment(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测虚拟环境"""
        try:
            # 检查是否在虚拟环境中
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            
            if not env_config.get('virtual_env', True):
                # 不要求虚拟环境
                return {
                    'status': 'success',
                    'in_virtual_env': in_venv,
                    'message': '虚拟环境检测跳过（配置允许）'
                }
            
            if in_venv:
                return {
                    'status': 'success',
                    'in_virtual_env': True,
                    'python_prefix': sys.prefix,
                    'message': '运行在虚拟环境中'
                }
            else:
                return {
                    'status': 'warning',
                    'in_virtual_env': False,
                    'message': '未在虚拟环境中运行，建议使用虚拟环境隔离依赖'
                }
                
        except Exception as e:
            logger.error(f"虚拟环境检测失败: {e}")
            return {
                'status': 'error',
                'message': f'虚拟环境检测失败: {str(e)}'
            }
    
    def _check_system_libraries(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测系统运行库"""
        try:
            required_libraries = env_config.get('system_libraries', [])
            results = {}
            
            for lib in required_libraries:
                lib_check = self._check_single_library(lib)
                results[lib] = lib_check
            
            # 分析整体状态
            error_count = sum(1 for r in results.values() if r.get('status') == 'error')
            warning_count = sum(1 for r in results.values() if r.get('status') == 'warning')
            
            if error_count > 0:
                overall_status = 'error'
            elif warning_count > 0:
                overall_status = 'warning'
            else:
                overall_status = 'success'
            
            return {
                'status': overall_status,
                'message': f'系统库检测完成: {len(required_libraries)} 个库',
                'details': results
            }
            
        except Exception as e:
            logger.error(f"系统库检测失败: {e}")
            return {
                'status': 'error',
                'message': f'系统库检测失败: {str(e)}'
            }
    
    def _check_single_library(self, library_name: str) -> Dict[str, Any]:
        """检测单个系统库"""
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                # Windows系统库检测
                return self._check_windows_library(library_name)
            elif system == 'linux':
                # Linux系统库检测
                return self._check_linux_library(library_name)
            elif system == 'darwin':
                # macOS系统库检测
                return self._check_macos_library(library_name)
            else:
                return {
                    'status': 'warning',
                    'message': f'未知操作系统: {system}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'库检测失败: {str(e)}'
            }
    
    def _check_windows_library(self, library_name: str) -> Dict[str, Any]:
        """检测Windows系统库"""
        common_libraries = {
            'msvc': {
                'check_method': 'registry',
                'registry_path': r'SOFTWARE\Microsoft\VisualStudio',
                'description': 'Microsoft Visual C++ Build Tools'
            },
            'directx': {
                'check_method': 'file',
                'file_paths': [
                    r'C:\Windows\System32\d3d11.dll',
                    r'C:\Windows\System32\dxgi.dll',
                    r'C:\Windows\SysWOW64\d3d11.dll'
                ],
                'description': 'DirectX Runtime'
            },
            'net_framework': {
                'check_method': 'registry',
                'registry_path': r'SOFTWARE\Microsoft\NET Framework Setup\NDP',
                'description': '.NET Framework'
            },
            'vulkan': {
                'check_method': 'file',
                'file_paths': [
                    r'C:\Windows\System32\vulkan-1.dll',
                    r'C:\Windows\SysWOW64\vulkan-1.dll'
                ],
                'description': 'Vulkan Runtime'
            }
        }
        
        if library_name not in common_libraries:
            return {
                'status': 'warning',
                'message': f'未知库: {library_name}'
            }
        
        lib_info = common_libraries[library_name]
        
        try:
            check_method = lib_info.get('check_method', 'command')
            
            if check_method == 'file':
                # 通过检查文件是否存在来判断
                file_paths = lib_info.get('file_paths', [])
                found = False
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        found = True
                        break
                
                if found:
                    return {
                        'status': 'success',
                        'message': f'{lib_info["description"]} 已安装'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'{lib_info["description"]} 未安装或未找到'
                    }
            
            elif check_method == 'registry':
                # 通过注册表检查
                registry_path = lib_info.get('registry_path', '')
                result = subprocess.run(
                    ['reg', 'query', f'HKLM\\{registry_path}'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
                )
                
                if result.returncode == 0:
                    return {
                        'status': 'success',
                        'message': f'{lib_info["description"]} 已安装'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'{lib_info["description"]} 未安装或未找到'
                    }
            
            else:
                # 默认命令检查（已废弃dxdiag等会弹窗的命令）
                return {
                    'status': 'warning',
                    'message': f'{lib_info["description"]} 检测方法未实现'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'message': f'{lib_info["description"]} 检测超时'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'{lib_info["description"]} 检测失败: {str(e)}'
            }
    
    def _check_linux_library(self, library_name: str) -> Dict[str, Any]:
        """检测Linux系统库"""
        # 简化的Linux库检测
        try:
            result = subprocess.run(
                ['which', library_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': f'{library_name} 已安装'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'{library_name} 未安装'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'{library_name} 检测失败: {str(e)}'
            }
    
    def _check_macos_library(self, library_name: str) -> Dict[str, Any]:
        """检测macOS系统库"""
        # 简化的macOS库检测
        try:
            result = subprocess.run(
                ['which', library_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': f'{library_name} 已安装'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'{library_name} 未安装'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'{library_name} 检测失败: {str(e)}'
            }
    
    def _check_project_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """检测项目特定依赖"""
        try:
            project_path = config.get('project', {}).get('paths', {}).get('install_path', '')
            if not project_path:
                return {
                    'status': 'skipped',
                    'message': '未指定项目安装路径，跳过项目依赖检测'
                }
            
            # 这里可以扩展为检查项目的requirements.txt或pyproject.toml
            # 目前返回基础信息
            return {
                'status': 'info',
                'message': '项目依赖检测待实现',
                'project_path': project_path
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'项目依赖检测失败: {str(e)}'
            }
    
    def _analyze_environment_status(self, results: Dict[str, Any]) -> str:
        """分析整体环境状态"""
        if not results:
            return 'unknown'
        
        critical_checks = ['python_version', 'virtual_environment']
        
        # 检查关键项目
        for check_name in critical_checks:
            if check_name in results:
                check_result = results[check_name]
                if check_result.get('status') == 'error':
                    return 'error'
        
        # 检查其他项目
        error_count = sum(1 for r in results.values() if r.get('status') == 'error')
        warning_count = sum(1 for r in results.values() if r.get('status') == 'warning')
        
        if error_count > 0:
            return 'error'
        elif warning_count > 0:
            return 'warning'
        else:
            return 'success'
    
    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取环境问题修复建议"""
        status = result.get('status', 'unknown')
        details = result.get('details', {})
        
        # 如果状态正常，返回空字符串（不显示建议）
        if status == 'success':
            return ""
        elif status == 'warning':
            suggestions = []
            
            # Python版本警告
            if details.get('python_version', {}).get('status') == 'warning':
                suggestions.append("建议升级Python版本以满足项目要求")
            
            # 虚拟环境警告
            if details.get('virtual_environment', {}).get('status') == 'warning':
                suggestions.append("建议使用虚拟环境隔离项目依赖")
            
            return "；".join(suggestions) if suggestions else "存在环境警告，建议检查相关配置"
        
        elif status == 'error':
            suggestions = []
            
            # Python版本错误
            python_version_detail = details.get('python_version', {})
            if python_version_detail.get('status') == 'error':
                current = python_version_detail.get('current_version', '未知')
                required = python_version_detail.get('required_version', '未知')
                suggestions.append(f"需要安装Python {required}（当前: {current}）")
            
            # 系统库错误
            system_libs_detail = details.get('system_libraries', {})
            if system_libs_detail.get('status') == 'error':
                failed_libs = [lib for lib, result in system_libs_detail.get('details', {}).items() 
                              if result.get('status') == 'error']
                if failed_libs:
                    suggestions.append(f"需要安装系统库: {', '.join(failed_libs)}")
            
            return "；".join(suggestions) if suggestions else "环境存在严重问题，请检查系统依赖和配置"
        
        else:
            return "环境状态未知，建议全面检查系统环境"