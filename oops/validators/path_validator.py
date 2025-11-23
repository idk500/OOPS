"""
路径验证器
基于知识库的路径规范进行验证
"""

import re
from pathlib import Path
from typing import Any, Dict, List


class PathValidator:
    """路径验证器 - 基于知识库规范"""

    def __init__(self):
        # 允许的字符（基于知识库）
        # Windows路径格式: C:\path\to\dir 或 C:/path/to/dir
        self.allowed_chars_pattern = re.compile(r"^[a-zA-Z]:[\\\/][a-zA-Z0-9_\-\\\/]+$")

        # 推荐的路径
        self.recommended_paths = [
            r"D:\ZZZ-OD",
            r"C:\Games\ZZZ-OD",
            r"D:\Games",
            r"E:\Projects",
        ]

        # 最大路径长度
        self.max_path_length = 100

    def validate_path(self, path: str) -> Dict[str, Any]:
        """验证路径是否符合规范

        Returns:
            {
                'valid': bool,
                'issues': List[str],
                'warnings': List[str],
                'recommendations': List[str]
            }
        """
        issues = []
        warnings = []
        recommendations = []

        # 检查中文字符
        if self._contains_chinese(path):
            issues.append("路径包含中文字符")
            recommendations.append("使用纯英文路径，例如: D:\\ZZZ-OD")

        # 检查空格
        if " " in path:
            issues.append("路径包含空格")
            recommendations.append("使用下划线或连字符代替空格")

        # 检查路径长度
        if len(path) > self.max_path_length:
            warnings.append(f"路径过长 ({len(path)} > {self.max_path_length})")
            recommendations.append("使用较短的路径名")

        # 检查特殊字符（排除Windows路径的冒号和斜杠）
        # 移除盘符和路径分隔符后检查
        path_without_drive = path[2:] if len(path) > 2 and path[1] == ":" else path
        path_clean = path_without_drive.replace("\\", "").replace("/", "")

        if not re.match(r"^[a-zA-Z0-9_\-]+$", path_clean):
            issues.append("路径包含不允许的特殊字符")
            recommendations.append("只使用字母、数字、下划线和连字符")

        # 检查是否在需要管理员权限的目录
        admin_required_paths = [
            r"C:\Windows",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]

        for admin_path in admin_required_paths:
            if path.lower().startswith(admin_path.lower()):
                warnings.append("路径位于需要管理员权限的目录")
                recommendations.append("选择用户目录或其他盘符")

        # 检查是否在推荐路径
        is_recommended = any(
            path.lower().startswith(rec_path.lower())
            for rec_path in self.recommended_paths
        )

        if not is_recommended and not issues:
            recommendations.append(
                f"推荐使用以下路径: {', '.join(self.recommended_paths[:2])}"
            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文字符"""
        return bool(re.search(r"[\u4e00-\u9fff]", text))

    def validate_username(self, username: str) -> Dict[str, Any]:
        """验证用户名是否符合规范（全英文无特殊字符）

        Args:
            username: 用户名

        Returns:
            {
                'valid': bool,
                'issues': List[str],
                'warnings': List[str],
                'recommendations': List[str]
            }
        """
        issues = []
        warnings = []
        recommendations = []

        # 检查是否为空
        if not username or username == "Unknown":
            warnings.append("无法获取用户名")
            return {
                "valid": True,
                "issues": issues,
                "warnings": warnings,
                "recommendations": recommendations,
            }

        # 检查中文字符
        if self._contains_chinese(username):
            issues.append("用户名包含中文字符")
            recommendations.append("Windows用户名建议使用纯英文，避免路径问题")

        # 检查空格
        if " " in username:
            issues.append("用户名包含空格")
            recommendations.append("用户名中的空格可能导致某些程序路径识别问题")

        # 检查特殊字符（只允许字母、数字、下划线、连字符）
        if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
            issues.append("用户名包含特殊字符")
            recommendations.append("建议用户名只包含字母、数字、下划线和连字符")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    def get_path_score(self, path: str) -> int:
        """评估路径质量（0-100分）"""
        score = 100
        validation = self.validate_path(path)

        # 每个问题扣30分
        score -= len(validation["issues"]) * 30

        # 每个警告扣10分
        score -= len(validation["warnings"]) * 10

        # 如果是推荐路径，加10分
        is_recommended = any(
            path.lower().startswith(rec_path.lower())
            for rec_path in self.recommended_paths
        )
        if is_recommended:
            score = min(100, score + 10)

        return max(0, score)

    def suggest_alternative_path(self, current_path: str) -> str:
        """建议替代路径"""
        # 提取项目名称
        path_obj = Path(current_path)
        project_name = path_obj.name

        # 清理项目名称（移除中文和空格）
        clean_name = re.sub(r"[\u4e00-\u9fff\s]", "", project_name)
        if not clean_name:
            clean_name = "Project"

        # 返回推荐路径
        return f"D:\\{clean_name}"


class HardwareValidator:
    """硬件配置验证器 - 基于知识库要求"""

    def __init__(self):
        # 最低配置要求（基于知识库）
        self.minimum_requirements = {
            "memory_gb": 8,
            "disk_type": "SSD",  # 推荐SSD，HDD可能异常
        }

        # 推荐配置
        self.recommended_requirements = {
            "desktop": {
                "cpu_generation": 8,  # 第八代i5及以上
                "memory_gb": 8,
                "gpu": "GTX1060",
            },
            "laptop": {
                "cpu_generation": 12,  # 第十二代i5及以上
                "memory_gb": 8,
                "gpu": "GTX1060",
            },
        }

    def validate_memory(self, memory_gb: float) -> Dict[str, Any]:
        """验证内存是否满足要求"""
        min_memory = self.minimum_requirements["memory_gb"]

        if memory_gb < min_memory:
            return {
                "valid": False,
                "message": f"内存不足: {memory_gb}GB < {min_memory}GB",
                "recommendation": f"建议至少{min_memory}GB内存",
            }

        return {
            "valid": True,
            "message": f"内存充足: {memory_gb}GB",
            "recommendation": None,
        }

    def validate_disk_type(self, disk_type: str) -> Dict[str, Any]:
        """验证磁盘类型"""
        recommended_type = self.minimum_requirements["disk_type"]

        if disk_type.upper() == "HDD":
            return {
                "valid": True,
                "warning": True,
                "message": "使用机械硬盘(HDD)可能会发生运行异常",
                "recommendation": "强烈建议使用固态硬盘(SSD)",
            }
        elif disk_type.upper() == "SSD":
            return {
                "valid": True,
                "warning": False,
                "message": "使用固态硬盘(SSD)，性能良好",
                "recommendation": None,
            }
        else:
            return {
                "valid": True,
                "warning": False,
                "message": f"磁盘类型: {disk_type}",
                "recommendation": "建议使用固态硬盘(SSD)",
            }


class GameSettingsValidator:
    """游戏设置验证器 - 基于知识库要求"""

    def __init__(self):
        # 分辨率要求
        self.aspect_ratio = "16:9"
        self.recommended_resolutions = [(1920, 1080), (2560, 1440), (3840, 2160)]

        # 显示模式
        self.recommended_window_mode = "windowed"

    def validate_resolution(self, width: int, height: int) -> Dict[str, Any]:
        """验证分辨率是否符合要求"""
        # 检查宽高比
        ratio = width / height
        target_ratio = 16 / 9

        if abs(ratio - target_ratio) > 0.01:
            return {
                "valid": False,
                "message": f"分辨率不是16:9: {width}x{height}",
                "recommendation": f"推荐使用16:9分辨率，如: 1920x1080",
            }

        # 检查是否是推荐分辨率
        is_recommended = (width, height) in self.recommended_resolutions

        return {
            "valid": True,
            "is_recommended": is_recommended,
            "message": f"分辨率符合要求: {width}x{height}",
            "recommendation": (
                "1920x1080窗口模式效果最佳" if not is_recommended else None
            ),
        }

    def validate_display_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """验证显示设置"""
        issues = []

        # 检查可能影响识别的设置
        problematic_settings = [
            "hdr",
            "color_profile",
            "night_mode",
            "eye_care_mode",
            "game_filter",
            "color_temperature",
        ]

        for setting in problematic_settings:
            if settings.get(setting, False):
                issues.append(f"检测到可能影响识别的设置: {setting}")

        if issues:
            return {
                "valid": False,
                "issues": issues,
                "recommendation": "关闭所有会改变画面像素值的功能",
            }

        return {"valid": True, "message": "显示设置正常", "recommendation": None}

    def validate_game_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证游戏配置"""
        issues = []
        warnings = []

        # 检查帧率设置
        if config.get("frame_rate") == "unlimited":
            warnings.append("不建议设置无限帧率")

        # 检查MOD
        if config.get("has_mods", False):
            issues.append("检测到MOD，可能导致脚本异常")

        # 检查画质
        quality = config.get("quality", "medium")
        if quality == "low":
            warnings.append("画质较低可能影响识别准确率")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "recommendation": "游戏画质越好，脚本出错几率越低",
        }
