"""
环境依赖检测器
检测系统级依赖，如MSVC、CUDA等
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
    """环境依赖检测器，专注于系统级依赖"""

    def __init__(self):
        super().__init__(
            name="environment_dependencies",
            description="检测环境依赖",
            severity="error",
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行环境依赖检测，专注于系统级依赖"""
        env_config = config.get("checks", {}).get("environment", {})
        if not env_config.get("enabled", False):
            return {"status": "skipped", "message": "环境检测已禁用"}

        results = {}

        # 系统运行库检测（专注于系统级依赖，如MSVC、CUDA等）
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
            "cuda": {
                "check_method": "registry",
                "registry_path": r"SOFTWARE\NVIDIA Corporation\NVIDIA GPU Computing Toolkit\CUDA",
                "description": "NVIDIA CUDA Toolkit",
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
            warning_count = sum(
                1 for r in results.values() if r.get("status") == "warning"
            )

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
            embedded_python_path = (
                Path(project_path) / ".install" / "python" / "python.exe"
            )

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
        """分析整体环境状态，专注于系统级依赖"""
        if not results:
            return "unknown"

        # 检查系统库状态
        system_libs = results.get("system_libraries", {})
        if system_libs.get("status") == "error":
            return "error"
        
        # 检查项目依赖状态
        project_deps = results.get("project_dependencies", {})
        if project_deps.get("status") == "error":
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
        """获取环境问题修复建议，专注于系统级依赖"""
        status = result.get("status", "unknown")
        details = result.get("details", {})

        # 如果状态正常，返回空字符串（不显示建议）
        if status == "success":
            return ""
        elif status == "warning":
            suggestions = []

            # 系统库警告
            system_libs_detail = details.get("system_libraries", {})
            if system_libs_detail.get("status") == "warning":
                warning_libs = [
                    lib
                    for lib, result in system_libs_detail.get("details", {}).items()
                    if result.get("status") == "warning"
                ]
                if warning_libs:
                    suggestions.append(f"系统库警告: {', '.join(warning_libs)}")

            # 项目依赖警告
            project_deps_detail = details.get("project_dependencies", {})
            if project_deps_detail.get("status") == "warning":
                suggestions.append("项目依赖存在警告，建议检查相关配置")

            return (
                "；".join(suggestions)
                if suggestions
                else "存在环境警告，建议检查相关配置"
            )

        elif status == "error":
            suggestions = []

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

            # 项目依赖错误
            project_deps_detail = details.get("project_dependencies", {})
            if project_deps_detail.get("status") == "error":
                suggestions.append("项目依赖存在错误，建议检查相关配置")

            return (
                "；".join(suggestions)
                if suggestions
                else "环境存在严重问题，请检查系统依赖和配置"
            )

        else:
            return "环境状态未知，建议全面检查系统环境"
