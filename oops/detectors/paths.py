"""
路径规范检测器
检测工程目录路径、权限、中文路径等问题
"""

import logging
import os
import platform
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class PathValidationDetector(DetectionRule):
    """路径规范检测器"""

    def __init__(self):
        super().__init__(
            name="path_validation", description="检测路径规范", severity="warning"
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行路径规范检测"""
        paths_config = config.get("checks", {}).get("paths", {})
        if not paths_config.get("enabled", False):
            return {"status": "skipped", "message": "路径检测已禁用"}

        project_config = config.get("project", {})
        paths_info = project_config.get("paths", {})
        install_path = paths_info.get("install_path", "")

        # 如果未指定路径，使用当前工作目录
        if not install_path:
            import os

            install_path = os.getcwd()
            logger.info(f"未指定安装路径，使用当前目录: {install_path}")

        results = {}

        # 检查安装路径是否存在
        path_exists_check = self._check_path_exists(install_path)
        results["path_exists"] = path_exists_check

        # 中文路径检测
        if paths_config.get("check_chinese_paths", True):
            chinese_path_check = self._check_chinese_paths(install_path)
            results["chinese_paths"] = chinese_path_check

        # 权限检查
        if paths_config.get("check_permissions", True):
            permissions_check = self._check_permissions(install_path)
            results["permissions"] = permissions_check

        # 路径长度检查
        if paths_config.get("check_path_length", True):
            path_length_check = self._check_path_length(install_path)
            results["path_length"] = path_length_check

        # 特殊字符检查
        special_chars_check = self._check_special_characters(install_path)
        results["special_characters"] = special_chars_check

        # 空格检查
        spaces_check = self._check_spaces_in_path(install_path)
        results["spaces"] = spaces_check

        # 默认游戏路径检查（仅作为信息提示）
        default_game_path = paths_config.get("default_game_path")
        if default_game_path:
            default_path_check = self._check_default_game_path(default_game_path)
            results["default_game_path"] = default_path_check

        # 分析整体路径状态
        overall_status = self._analyze_path_status(results)

        return {
            "status": overall_status,
            "message": f"路径检测完成，共执行 {len(results)} 项检查",
            "details": results,
            "install_path": install_path,
        }

    def _check_path_exists(self, install_path: str) -> Dict[str, Any]:
        """检查路径是否存在"""
        try:
            path = Path(install_path)
            if path.exists():
                return {
                    "status": "success",
                    "message": f"路径存在: {install_path}",
                    "absolute_path": str(path.absolute()),
                }
            else:
                return {
                    "status": "error",
                    "message": f"路径不存在: {install_path}",
                    "fix_suggestion": "请检查安装路径是否正确，或重新安装项目",
                }
        except Exception as e:
            return {"status": "error", "message": f"路径存在性检查失败: {str(e)}"}

    def _check_chinese_paths(self, install_path: str) -> Dict[str, Any]:
        """检查路径是否包含中文字符"""
        try:
            # 检查路径中的每个部分是否包含中文字符
            path_parts = install_path.split(os.sep)
            chinese_parts = []

            for part in path_parts:
                if self._contains_chinese(part):
                    chinese_parts.append(part)

            if chinese_parts:
                return {
                    "status": "error",
                    "message": f'路径包含中文字符: {", ".join(chinese_parts)}',
                    "chinese_parts": chinese_parts,
                    "fix_suggestion": "建议将项目安装在纯英文路径下，避免编码问题",
                }
            else:
                return {"status": "success", "message": "路径不包含中文字符"}

        except Exception as e:
            return {"status": "error", "message": f"中文路径检查失败: {str(e)}"}

    def _check_permissions(self, install_path: str) -> Dict[str, Any]:
        """检查路径权限"""
        try:
            path = Path(install_path)

            if not path.exists():
                return {"status": "skipped", "message": "路径不存在，跳过权限检查"}

            # 检查读取权限
            if not os.access(install_path, os.R_OK):
                return {
                    "status": "error",
                    "message": "路径缺少读取权限",
                    "fix_suggestion": "请以管理员权限运行程序，或调整路径权限",
                }

            # 检查写入权限
            if not os.access(install_path, os.W_OK):
                return {
                    "status": "warning",
                    "message": "路径缺少写入权限",
                    "fix_suggestion": "某些功能可能需要写入权限，建议调整路径权限",
                }

            # 检查执行权限（对于目录）
            if path.is_dir() and not os.access(install_path, os.X_OK):
                return {
                    "status": "warning",
                    "message": "目录缺少执行权限",
                    "fix_suggestion": "目录需要执行权限才能访问内容",
                }

            return {"status": "success", "message": "路径权限正常"}

        except Exception as e:
            return {"status": "error", "message": f"权限检查失败: {str(e)}"}

    def _check_path_length(self, install_path: str) -> Dict[str, Any]:
        """检查路径长度"""
        try:
            # Windows系统有260字符路径限制
            if platform.system().lower() == "windows":
                max_length = 260
                current_length = len(install_path)

                if current_length > max_length - 50:  # 预留一些空间
                    return {
                        "status": "warning",
                        "message": f"路径长度较长: {current_length} 字符 (Windows限制: {max_length})",
                        "current_length": current_length,
                        "max_recommended": max_length - 50,
                        "fix_suggestion": "建议使用较短的路径，避免Windows路径长度限制",
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"路径长度正常: {current_length} 字符",
                    }
            else:
                # 其他系统路径限制较宽松
                current_length = len(install_path)
                return {
                    "status": "info",
                    "message": f"路径长度: {current_length} 字符 (非Windows系统)",
                }

        except Exception as e:
            return {"status": "error", "message": f"路径长度检查失败: {str(e)}"}

    def _check_special_characters(self, install_path: str) -> Dict[str, Any]:
        """检查特殊字符"""
        try:
            # 常见问题字符（排除Windows路径中合法的冒号）
            problematic_chars = ["<", ">", '"', "|", "?", "*"]
            found_chars = []

            # 移除盘符后检查（Windows: C:\path）
            path_to_check = install_path
            if len(install_path) > 2 and install_path[1] == ":":
                path_to_check = install_path[2:]  # 跳过 "C:"

            for char in problematic_chars:
                if char in path_to_check:
                    found_chars.append(char)

            if found_chars:
                return {
                    "status": "error",
                    "message": f'路径包含特殊字符: {", ".join(found_chars)}',
                    "problematic_chars": found_chars,
                    "fix_suggestion": '路径中不应包含以下字符: < > " | ? *',
                }
            else:
                return {"status": "success", "message": "路径不包含问题特殊字符"}

        except Exception as e:
            return {"status": "error", "message": f"特殊字符检查失败: {str(e)}"}

    def _check_spaces_in_path(self, install_path: str) -> Dict[str, Any]:
        """检查路径中的空格"""
        try:
            if " " in install_path:
                return {
                    "status": "warning",
                    "message": "路径包含空格",
                    "fix_suggestion": "某些程序可能对路径中的空格处理不当，建议使用下划线或连字符代替空格",
                }
            else:
                return {"status": "success", "message": "路径不包含空格"}

        except Exception as e:
            return {"status": "error", "message": f"空格检查失败: {str(e)}"}

    def _contains_chinese(self, text: str) -> bool:
        """检查字符串是否包含中文字符"""
        try:
            for char in text:
                if "\u4e00" <= char <= "\u9fff":
                    return True
            return False
        except:
            return False

    def _analyze_path_status(self, results: Dict[str, Any]) -> str:
        """分析整体路径状态"""
        if not results:
            return "unknown"

        # 关键检查项
        critical_checks = ["path_exists", "chinese_paths", "special_characters"]

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

    def _check_default_game_path(self, default_path: str) -> Dict[str, Any]:
        """检查默认游戏路径（仅作为信息提示）"""
        try:
            path = Path(default_path)
            exists = path.exists() and path.is_file()

            if exists:
                return {
                    "status": "info",
                    "message": f"默认游戏路径存在: {default_path}",
                }
            else:
                return {
                    "status": "info",
                    "message": f"默认游戏路径不存在: {default_path}",
                    "note": "这不影响脚本运行，如果游戏安装在其他位置，请在配置文件中指定",
                }
        except Exception as e:
            logger.debug(f"检查默认游戏路径失败: {e}")
            return {"status": "info", "message": "无法检查默认游戏路径"}

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取路径问题修复建议"""
        status = result.get("status", "unknown")
        details = result.get("details", {})

        # 如果状态正常，返回空字符串（不显示建议）
        if status == "success":
            return ""
        elif status == "warning":
            suggestions = []

            # 路径长度警告
            if details.get("path_length", {}).get("status") == "warning":
                suggestions.append("建议缩短安装路径长度")

            # 权限警告
            if details.get("permissions", {}).get("status") == "warning":
                suggestions.append("建议检查路径写入和执行权限")

            # 空格警告
            if details.get("spaces", {}).get("status") == "warning":
                suggestions.append("建议移除路径中的空格")

            return (
                "；".join(suggestions)
                if suggestions
                else "存在路径规范警告，建议优化路径设置"
            )

        elif status == "error":
            suggestions = []

            # 路径不存在
            if details.get("path_exists", {}).get("status") == "error":
                suggestions.append("请确保项目安装路径存在且正确")

            # 中文路径错误
            if details.get("chinese_paths", {}).get("status") == "error":
                suggestions.append("请将项目移动到纯英文路径下")

            # 特殊字符错误
            if details.get("special_characters", {}).get("status") == "error":
                suggestions.append("请移除路径中的特殊字符")

            # 权限错误
            if details.get("permissions", {}).get("status") == "error":
                suggestions.append("请确保有足够的路径访问权限")

            return (
                "；".join(suggestions)
                if suggestions
                else "路径存在严重问题，请重新选择安装位置"
            )

        else:
            return "路径状态未知，建议检查安装路径设置"


class AdvancedPathDetector(PathValidationDetector):
    """高级路径检测器 - 包含更多路径相关检查"""

    def __init__(self):
        super().__init__()
        self.name = "advanced_path_validation"
        self.description = "高级路径规范检测"

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行高级路径检测"""
        basic_result = super().check(config)

        if basic_result.get("status") == "skipped":
            return basic_result

        install_path = basic_result.get("install_path", "")
        if not install_path:
            return basic_result

        # 添加高级检查
        advanced_results = basic_result.get("details", {}).copy()

        # 磁盘空间检查
        disk_space_check = self._check_disk_space(install_path)
        advanced_results["disk_space"] = disk_space_check

        # 路径符号链接检查
        symlink_check = self._check_symlinks(install_path)
        advanced_results["symlinks"] = symlink_check

        # 文件系统类型检查
        filesystem_check = self._check_filesystem(install_path)
        advanced_results["filesystem"] = filesystem_check

        # 更新整体状态
        overall_status = self._analyze_path_status(advanced_results)

        return {
            "status": overall_status,
            "message": f"高级路径检测完成，共执行 {len(advanced_results)} 项检查",
            "details": advanced_results,
            "install_path": install_path,
        }

    def _check_disk_space(self, install_path: str) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            if platform.system().lower() == "windows":
                import ctypes

                # Windows系统磁盘空间检查
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)

                drive = os.path.splitdrive(install_path)[0]
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    drive, None, ctypes.byref(total_bytes), ctypes.byref(free_bytes)
                )

                free_gb = free_bytes.value / (1024**3)
                total_gb = total_bytes.value / (1024**3)

                if free_gb < 1:  # 小于1GB
                    return {
                        "status": "error",
                        "message": f"磁盘空间严重不足: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                        "total_space_gb": total_gb,
                        "fix_suggestion": "请清理磁盘空间，至少保留1GB可用空间",
                    }
                elif free_gb < 5:  # 小于5GB
                    return {
                        "status": "warning",
                        "message": f"磁盘空间紧张: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                        "total_space_gb": total_gb,
                        "fix_suggestion": "建议清理磁盘空间，确保有足够空间运行程序",
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"磁盘空间充足: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                        "total_space_gb": total_gb,
                    }
            else:
                # Linux/macOS系统磁盘空间检查
                statvfs = os.statvfs(install_path)
                free_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)

                if free_gb < 1:
                    return {
                        "status": "error",
                        "message": f"磁盘空间严重不足: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                        "fix_suggestion": "请清理磁盘空间",
                    }
                elif free_gb < 5:
                    return {
                        "status": "warning",
                        "message": f"磁盘空间紧张: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                        "fix_suggestion": "建议清理磁盘空间",
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"磁盘空间充足: {free_gb:.2f} GB 可用",
                        "free_space_gb": free_gb,
                    }

        except Exception as e:
            return {"status": "error", "message": f"磁盘空间检查失败: {str(e)}"}

    def _check_symlinks(self, install_path: str) -> Dict[str, Any]:
        """检查符号链接"""
        try:
            path = Path(install_path)

            # 检查路径本身是否为符号链接
            if path.is_symlink():
                return {
                    "status": "warning",
                    "message": "安装路径是符号链接",
                    "target": str(path.resolve()),
                    "fix_suggestion": "符号链接可能导致路径解析问题，建议使用实际路径",
                }

            # 检查路径中是否包含符号链接
            current_path = Path("/")
            for part in path.parts:
                current_path = current_path / part
                if current_path.is_symlink():
                    return {
                        "status": "warning",
                        "message": f"路径包含符号链接: {current_path}",
                        "symlink_path": str(current_path),
                        "target": str(current_path.resolve()),
                        "fix_suggestion": "符号链接可能导致路径解析问题",
                    }

            return {"status": "success", "message": "路径不包含符号链接"}

        except Exception as e:
            return {"status": "error", "message": f"符号链接检查失败: {str(e)}"}

    def _check_filesystem(self, install_path: str) -> Dict[str, Any]:
        """检查文件系统类型"""
        try:
            if platform.system().lower() == "windows":
                # Windows系统文件系统检查
                import ctypes

                drive = os.path.splitdrive(install_path)[0]
                filesystem = ctypes.create_unicode_buffer(32)

                if ctypes.windll.kernel32.GetVolumeInformationW(
                    drive,
                    None,
                    0,
                    None,
                    None,
                    None,
                    filesystem,
                    ctypes.sizeof(filesystem),
                ):
                    fs_type = filesystem.value

                    # 检查是否为推荐的文件系统
                    if fs_type in ["NTFS", "exFAT"]:
                        return {
                            "status": "success",
                            "message": f"文件系统类型: {fs_type}",
                            "filesystem": fs_type,
                        }
                    else:
                        return {
                            "status": "warning",
                            "message": f"文件系统类型: {fs_type} (非推荐类型)",
                            "filesystem": fs_type,
                            "fix_suggestion": "建议使用NTFS或exFAT文件系统以获得更好的兼容性",
                        }
                else:
                    return {"status": "error", "message": "无法获取文件系统信息"}
            else:
                # 非Windows系统，简化处理
                return {"status": "info", "message": "文件系统检查仅支持Windows系统"}

        except Exception as e:
            return {"status": "error", "message": f"文件系统检查失败: {str(e)}"}
