"""
环境依赖检测器
检测Python环境、系统运行库、虚拟环境等依赖项
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class EnvironmentDependencyDetector(DetectionRule):
    """环境依赖检测器"""

    def __init__(self):
        super().__init__(
            name="environment_dependencies",
            description="检测环境依赖",
            severity="error",
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行环境依赖检测"""
        env_config = config.get("checks", {}).get("environment", {})
        if not env_config.get("enabled", False):
            return {"status": "skipped", "message": "环境检测已禁用"}

        results = {}

        # Python版本检测
        python_version_check = self._check_python_version(env_config)
        results["python_version"] = python_version_check

        # 虚拟环境检测
        virtual_env_check = self._check_virtual_environment(env_config)
        results["virtual_environment"] = virtual_env_check

        # 系统运行库检测
        system_libraries_check = self._check_system_libraries(env_config)
        results["system_libraries"] = system_libraries_check

        # 项目特定依赖检测
        project_deps_check = self._check_project_dependencies(config)
        results["project_dependencies"] = project_deps_check

        # 分析整体环境状态
        overall_status = self._analyze_environment_status(results)

        return {
            "status": overall_status,
            "message": f"环境检测完成，共执行 {len(results)} 项检查",
            "details": results,
        }

    def _check_python_version(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测Python版本兼容性"""
        try:
            current_version = sys.version_info
            required_version = env_config.get("python_version", ">=3.8")

            # 解析版本要求
            if required_version.startswith(">="):
                min_version = tuple(map(int, required_version[2:].split(".")))
                is_compatible = current_version >= min_version
            elif required_version.startswith("=="):
                exact_version = tuple(map(int, required_version[2:].split(".")))
                is_compatible = (
                    current_version[:2] == exact_version[:2]
                )  # 只比较主次版本
            else:
                # 默认要求 >= 3.8
                is_compatible = current_version >= (3, 8)

            if is_compatible:
                return {
                    "status": "success",
                    "current_version": f"{current_version.major}.{current_version.minor}.{current_version.micro}",
                    "required_version": required_version,
                    "message": f"Python版本兼容: {current_version.major}.{current_version.minor}.{current_version.micro}",
                }
            else:
                return {
                    "status": "error",
                    "current_version": f"{current_version.major}.{current_version.minor}.{current_version.micro}",
                    "required_version": required_version,
                    "message": f"Python版本不兼容: 当前 {current_version.major}.{current_version.minor}.{current_version.micro}, 需要 {required_version}",
                }

        except Exception as e:
            logger.error(f"Python版本检测失败: {e}")
            return {"status": "error", "message": f"Python版本检测失败: {str(e)}"}

    def _is_valid_venv(self, venv_path: Path) -> bool:
        """验证目录是否是有效的虚拟环境

        Args:
            venv_path: 虚拟环境路径

        Returns:
            是否是有效的虚拟环境
        """
        try:
            system = platform.system().lower()

            if system == "windows":
                # Windows: 检查 Scripts/activate.bat 或 Scripts/Activate.ps1
                activate_bat = venv_path / "Scripts" / "activate.bat"
                activate_ps1 = venv_path / "Scripts" / "Activate.ps1"
                python_exe = venv_path / "Scripts" / "python.exe"

                return (
                    activate_bat.exists() or activate_ps1.exists()
                ) and python_exe.exists()
            else:
                # Linux/macOS: 检查 bin/activate
                activate_sh = venv_path / "bin" / "activate"
                python_bin = venv_path / "bin" / "python"

                return activate_sh.exists() and python_bin.exists()

        except Exception as e:
            logger.debug(f"验证虚拟环境失败: {e}")
            return False

    def _check_virtual_environment(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测虚拟环境"""
        try:
            # 检查是否在虚拟环境中运行
            in_venv = hasattr(sys, "real_prefix") or (
                hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
            )

            if not env_config.get("virtual_env", True):
                # 不要求虚拟环境
                return {
                    "status": "success",
                    "in_virtual_env": in_venv,
                    "message": "虚拟环境检测跳过（配置允许）",
                }

            # 检查项目目录下是否存在虚拟环境
            project_path = env_config.get("project_path")
            venv_exists = False
            venv_path = None

            if project_path:
                # 方法1: 检查常见的虚拟环境目录名
                common_venv_names = [".venv", "venv", "env", ".env"]
                for venv_name in common_venv_names:
                    potential_venv = Path(project_path) / venv_name
                    logger.debug(
                        f"检查虚拟环境: {potential_venv}, 存在: {potential_venv.exists()}"
                    )
                    if potential_venv.exists() and potential_venv.is_dir():
                        # 验证是否真的是虚拟环境（检查activate脚本）
                        is_valid = self._is_valid_venv(potential_venv)
                        logger.debug(f"虚拟环境验证结果: {is_valid}")
                        if is_valid:
                            venv_exists = True
                            venv_path = str(potential_venv)
                            logger.info(f"找到虚拟环境: {venv_path}")
                            break

                # 方法2: 如果方法1没找到，扫描项目根目录查找任何包含activate脚本的目录
                if not venv_exists:
                    try:
                        for item in Path(project_path).iterdir():
                            if item.is_dir() and self._is_valid_venv(item):
                                venv_exists = True
                                venv_path = str(item)
                                break
                    except (PermissionError, OSError):
                        pass

            # 如果项目目录存在虚拟环境，认为配置正确
            if venv_exists:
                return {
                    "status": "success",
                    "in_virtual_env": in_venv,
                    "venv_exists": True,
                    "venv_path": venv_path,
                    "message": f"项目已配置虚拟环境: {venv_path}",
                }
            elif in_venv:
                # 当前在虚拟环境中运行
                return {
                    "status": "success",
                    "in_virtual_env": True,
                    "python_prefix": sys.prefix,
                    "message": "运行在虚拟环境中",
                }
            else:
                return {
                    "status": "warning",
                    "in_virtual_env": False,
                    "venv_exists": False,
                    "message": "未检测到虚拟环境，建议使用虚拟环境隔离依赖",
                }

        except Exception as e:
            logger.error(f"虚拟环境检测失败: {e}")
            return {"status": "error", "message": f"虚拟环境检测失败: {str(e)}"}

    def _check_system_libraries(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """检测系统运行库"""
        try:
            required_libraries = env_config.get("system_libraries", [])
            results = {}

            for lib in required_libraries:
                lib_check = self._check_single_library(lib)
                results[lib] = lib_check

            # 分析整体状态
            error_count = sum(1 for r in results.values() if r.get("status") == "error")
            warning_count = sum(
                1 for r in results.values() if r.get("status") == "warning"
            )

            if error_count > 0:
                overall_status = "error"
            elif warning_count > 0:
                overall_status = "warning"
            else:
                overall_status = "success"

            return {
                "status": overall_status,
                "message": f"系统库检测完成: {len(required_libraries)} 个库",
                "details": results,
            }

        except Exception as e:
            logger.error(f"系统库检测失败: {e}")
            return {"status": "error", "message": f"系统库检测失败: {str(e)}"}

    def _check_single_library(self, library_name: str) -> Dict[str, Any]:
        """检测单个系统库"""
        try:
            system = platform.system().lower()

            if system == "windows":
                # Windows系统库检测
                return self._check_windows_library(library_name)
            elif system == "linux":
                # Linux系统库检测
                return self._check_linux_library(library_name)
            elif system == "darwin":
                # macOS系统库检测
                return self._check_macos_library(library_name)
            else:
                return {"status": "warning", "message": f"未知操作系统: {system}"}

        except Exception as e:
            return {"status": "error", "message": f"库检测失败: {str(e)}"}

    def _check_windows_library(self, library_name: str) -> Dict[str, Any]:
        """检测Windows系统库"""
        common_libraries = {
            "msvc": {
                "check_method": "registry",
                "registry_path": r"SOFTWARE\Microsoft\VisualStudio",
                "description": "Microsoft Visual C++ Build Tools",
            },
            "directx": {
                "check_method": "file",
                "file_paths": [
                    r"C:\Windows\System32\d3d11.dll",
                    r"C:\Windows\System32\dxgi.dll",
                    r"C:\Windows\SysWOW64\d3d11.dll",
                ],
                "description": "DirectX Runtime",
            },
            "net_framework": {
                "check_method": "registry",
                "registry_path": r"SOFTWARE\Microsoft\NET Framework Setup\NDP",
                "description": ".NET Framework",
            },
            "vulkan": {
                "check_method": "file",
                "file_paths": [
                    r"C:\Windows\System32\vulkan-1.dll",
                    r"C:\Windows\SysWOW64\vulkan-1.dll",
                ],
                "description": "Vulkan Runtime",
            },
        }

        if library_name not in common_libraries:
            return {"status": "warning", "message": f"未知库: {library_name}"}

        lib_info = common_libraries[library_name]

        try:
            check_method = lib_info.get("check_method", "command")

            if check_method == "file":
                # 通过检查文件是否存在来判断
                file_paths = lib_info.get("file_paths", [])
                found = False
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        found = True
                        break

                if found:
                    return {
                        "status": "success",
                        "message": f'{lib_info["description"]} 已安装',
                    }
                else:
                    return {
                        "status": "error",
                        "message": f'{lib_info["description"]} 未安装或未找到',
                    }

            elif check_method == "registry":
                # 通过注册表检查
                registry_path = lib_info.get("registry_path", "")
                result = subprocess.run(
                    ["reg", "query", f"HKLM\\{registry_path}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=(
                        subprocess.CREATE_NO_WINDOW
                        if platform.system().lower() == "windows"
                        else 0
                    ),
                )

                if result.returncode == 0:
                    return {
                        "status": "success",
                        "message": f'{lib_info["description"]} 已安装',
                    }
                else:
                    return {
                        "status": "error",
                        "message": f'{lib_info["description"]} 未安装或未找到',
                    }

            else:
                # 默认命令检查（已废弃dxdiag等会弹窗的命令）
                return {
                    "status": "warning",
                    "message": f'{lib_info["description"]} 检测方法未实现',
                }

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f'{lib_info["description"]} 检测超时'}
        except Exception as e:
            return {
                "status": "error",
                "message": f'{lib_info["description"]} 检测失败: {str(e)}',
            }

    def _check_linux_library(self, library_name: str) -> Dict[str, Any]:
        """检测Linux系统库"""
        # 简化的Linux库检测
        try:
            result = subprocess.run(
                ["which", library_name], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                return {"status": "success", "message": f"{library_name} 已安装"}
            else:
                return {"status": "error", "message": f"{library_name} 未安装"}

        except Exception as e:
            return {"status": "error", "message": f"{library_name} 检测失败: {str(e)}"}

    def _check_macos_library(self, library_name: str) -> Dict[str, Any]:
        """检测macOS系统库"""
        # 简化的macOS库检测
        try:
            result = subprocess.run(
                ["which", library_name], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                return {"status": "success", "message": f"{library_name} 已安装"}
            else:
                return {"status": "error", "message": f"{library_name} 未安装"}

        except Exception as e:
            return {"status": "error", "message": f"{library_name} 检测失败: {str(e)}"}

    def _check_project_dependencies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """检测项目特定依赖和工具"""
        try:
            project_path = (
                config.get("project", {}).get("paths", {}).get("install_path", "")
            )
            if not project_path:
                return {
                    "status": "skipped",
                    "message": "未指定项目安装路径，跳过项目依赖检测",
                }

            results = {}
            
            # 检测 Git 工具
            git_check = self._check_git_tool(project_path)
            results["git"] = git_check
            
            # 检测嵌入式 Python（如 OneDragon 项目）
            embedded_python_check = self._check_embedded_python(project_path)
            if embedded_python_check.get("status") != "skipped":
                results["embedded_python"] = embedded_python_check
            
            # 分析整体状态
            error_count = sum(1 for r in results.values() if r.get("status") == "error")
            warning_count = sum(1 for r in results.values() if r.get("status") == "warning")
            
            if error_count > 0:
                overall_status = "error"
                message = f"项目依赖检测发现 {error_count} 个问题"
            elif warning_count > 0:
                overall_status = "warning"
                message = f"项目依赖检测发现 {warning_count} 个警告"
            else:
                overall_status = "success"
                message = "项目依赖检测通过"

            return {
                "status": overall_status,
                "message": message,
                "details": results,
            }

        except Exception as e:
            return {"status": "error", "message": f"项目依赖检测失败: {str(e)}"}
    
    def _check_git_tool(self, project_path: str) -> Dict[str, Any]:
        """检测 Git 工具（系统 Git 或嵌入式 MinGit）"""
        try:
            git_info = {
                "system_git": False,
                "embedded_git": False,
                "git_version": None,
                "git_path": None,
            }
            
            # 检查嵌入式 MinGit（如 OneDragon 项目）
            mingit_path = Path(project_path) / ".install" / "MinGit" / "bin" / "git.exe"
            if mingit_path.exists():
                git_info["embedded_git"] = True
                git_info["git_path"] = str(mingit_path)
                try:
                    result = subprocess.run(
                        [str(mingit_path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        git_info["git_version"] = result.stdout.strip()
                except Exception as e:
                    logger.debug(f"获取 MinGit 版本失败: {e}")
            
            # 检查系统 Git
            try:
                result = subprocess.run(
                    ["git", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    git_info["system_git"] = True
                    if not git_info["git_version"]:
                        git_info["git_version"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"检测系统 Git 失败: {e}")
            
            # 判断状态
            if git_info["embedded_git"] or git_info["system_git"]:
                git_type = []
                if git_info["embedded_git"]:
                    git_type.append("嵌入式 Git")
                if git_info["system_git"]:
                    git_type.append("系统 Git")
                
                return {
                    "status": "success",
                    "message": f"Git 工具可用: {', '.join(git_type)}",
                    "details": git_info,
                }
            else:
                return {
                    "status": "warning",
                    "message": "未检测到 Git 工具",
                    "details": git_info,
                }
                
        except Exception as e:
            logger.error(f"Git 工具检测失败: {e}")
            return {"status": "error", "message": f"Git 工具检测失败: {str(e)}"}
    
    def _check_embedded_python(self, project_path: str) -> Dict[str, Any]:
        """检测嵌入式 Python（如 OneDragon 项目的 .install/python）"""
        try:
            embedded_python_path = Path(project_path) / ".install" / "python" / "python.exe"
            
            if not embedded_python_path.exists():
                return {"status": "skipped", "message": "无嵌入式 Python"}
            
            python_info = {
                "path": str(embedded_python_path),
                "version": None,
            }
            
            try:
                result = subprocess.run(
                    [str(embedded_python_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    python_info["version"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"获取嵌入式 Python 版本失败: {e}")
            
            return {
                "status": "success",
                "message": f"嵌入式 Python 可用: {python_info['version'] or '版本未知'}",
                "details": python_info,
            }
            
        except Exception as e:
            logger.error(f"嵌入式 Python 检测失败: {e}")
            return {"status": "error", "message": f"嵌入式 Python 检测失败: {str(e)}"}

    def _analyze_environment_status(self, results: Dict[str, Any]) -> str:
        """分析整体环境状态"""
        if not results:
            return "unknown"

        critical_checks = ["python_version", "virtual_environment"]

        # 检查关键项目
        for check_name in critical_checks:
            if check_name in results:
                check_result = results[check_name]
                if check_result.get("status") == "error":
                    return "error"

        # 检查其他项目
        error_count = sum(1 for r in results.values() if r.get("status") == "error")
        warning_count = sum(1 for r in results.values() if r.get("status") == "warning")

        if error_count > 0:
            return "error"
        elif warning_count > 0:
            return "warning"
        else:
            return "success"

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取环境问题修复建议"""
        status = result.get("status", "unknown")
        details = result.get("details", {})

        # 如果状态正常，返回空字符串（不显示建议）
        if status == "success":
            return ""
        elif status == "warning":
            suggestions = []

            # Python版本警告
            if details.get("python_version", {}).get("status") == "warning":
                suggestions.append("建议升级Python版本以满足项目要求")

            # 虚拟环境警告
            if details.get("virtual_environment", {}).get("status") == "warning":
                suggestions.append("建议使用虚拟环境隔离项目依赖")

            return (
                "；".join(suggestions)
                if suggestions
                else "存在环境警告，建议检查相关配置"
            )

        elif status == "error":
            suggestions = []

            # Python版本错误
            python_version_detail = details.get("python_version", {})
            if python_version_detail.get("status") == "error":
                current = python_version_detail.get("current_version", "未知")
                required = python_version_detail.get("required_version", "未知")
                suggestions.append(f"需要安装Python {required}（当前: {current}）")

            # 系统库错误
            system_libs_detail = details.get("system_libraries", {})
            if system_libs_detail.get("status") == "error":
                failed_libs = [
                    lib
                    for lib, result in system_libs_detail.get("details", {}).items()
                    if result.get("status") == "error"
                ]
                if failed_libs:
                    suggestions.append(f"需要安装系统库: {', '.join(failed_libs)}")

            return (
                "；".join(suggestions)
                if suggestions
                else "环境存在严重问题，请检查系统依赖和配置"
            )

        else:
            return "环境状态未知，建议全面检查系统环境"
