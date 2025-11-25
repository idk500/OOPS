"""
路径解析工具
支持自动检测、环境变量、相对路径等
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PathResolver:
    """路径解析器 - 支持多种路径配置方式"""

    @staticmethod
    def resolve_path(
        path_config: str, base_dir: Optional[str] = None, project_name: str = ""
    ) -> Optional[str]:
        """
        解析路径配置

        Args:
            path_config: 路径配置字符串
            base_dir: 基准目录（用于相对路径）
            project_name: 项目名称（用于自动检测）

        Returns:
            解析后的绝对路径，如果无法解析则返回 None
        """
        if not path_config or path_config.lower() in ["auto", "none", "null"]:
            # 自动检测模式
            return PathResolver._auto_detect_project_path(project_name)

        # 处理环境变量
        path_config = PathResolver._expand_env_vars(path_config)

        # 转换为 Path 对象
        path = Path(path_config)

        # 如果是相对路径，转换为绝对路径
        if not path.is_absolute():
            if base_dir:
                path = Path(base_dir) / path
            else:
                path = Path.cwd() / path

        # 规范化路径
        try:
            path = path.resolve()
            if path.exists():
                return str(path)
            else:
                logger.warning(f"路径不存在: {path}")
                return str(path)  # 返回路径，即使不存在
        except Exception as e:
            logger.error(f"路径解析失败: {path_config}, 错误: {e}")
            return None

    @staticmethod
    def _expand_env_vars(path_str: str) -> str:
        """展开环境变量"""

        # 支持 ${VAR} 和 %VAR% 两种格式
        def replace_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        # 替换 ${VAR} 格式
        path_str = re.sub(r"\$\{([^}]+)\}", replace_var, path_str)
        # 替换 %VAR% 格式
        path_str = re.sub(r"%([^%]+)%", replace_var, path_str)
        # 展开 ~ 为用户目录
        path_str = os.path.expanduser(path_str)

        return path_str

    @staticmethod
    def _auto_detect_project_path(project_name: str = "") -> Optional[str]:
        """
        自动检测项目路径

        检测策略：
        1. 检查当前目录是否包含项目标识文件
        2. 检查父目录
        3. 检查常见安装位置
        """
        # 项目标识文件（根据项目类型不同）
        identifier_files = {
            "zenless_zone_zero": [
                "OneDragon-Launcher.exe",
                "OneDragon-Installer.exe",
                "src/zzz_od",
            ],
            "generic": ["pyproject.toml", "requirements.txt", "setup.py"],
        }

        # 获取当前项目的标识文件
        identifiers = identifier_files.get(
            project_name, identifier_files.get("generic", [])
        )

        # 1. 检查当前目录
        current_dir = Path.cwd()
        if PathResolver._check_project_dir(current_dir, identifiers):
            logger.info(f"自动检测到项目路径: {current_dir}")
            return str(current_dir)

        # 2. 检查父目录（最多向上3层）
        try:
            for i in range(1, 4):
                if i - 1 < len(current_dir.parents):
                    parent_dir = current_dir.parents[i - 1]
                    if PathResolver._check_project_dir(parent_dir, identifiers):
                        logger.info(f"自动检测到项目路径: {parent_dir}")
                        return str(parent_dir)
        except IndexError:
            pass  # 已经到达根目录

        # 3. 检查同级目录（常见的项目命名）
        if project_name == "zenless_zone_zero":
            possible_names = [
                "ZenlessZoneZero-OneDragon",
                "ZZZ-OneDragon",
                "ZZZ-1D",
                "zzz-od",
            ]
            parent = current_dir.parent
            for name in possible_names:
                candidate = parent / name
                if PathResolver._check_project_dir(candidate, identifiers):
                    logger.info(f"自动检测到项目路径: {candidate}")
                    return str(candidate)

        # 4. 检查环境变量
        env_vars = {
            "zenless_zone_zero": ["ZZZ_INSTALL_PATH", "ONEDRAGON_PATH"],
            "generic": ["PROJECT_PATH"],
        }
        for var in env_vars.get(project_name, env_vars.get("generic", [])):
            if var in os.environ:
                path = Path(os.environ[var])
                if path.exists():
                    logger.info(f"从环境变量 {var} 检测到项目路径: {path}")
                    return str(path)

        logger.warning(f"无法自动检测项目路径: {project_name}")
        return None

    @staticmethod
    def _check_project_dir(directory: Path, identifiers: list) -> bool:
        """检查目录是否包含项目标识文件"""
        if not directory.exists():
            return False

        for identifier in identifiers:
            check_path = directory / identifier
            if check_path.exists():
                return True

        return False

    @staticmethod
    def resolve_config_path(
        install_path: str, config_path_config: str = ""
    ) -> Optional[str]:
        """
        解析配置文件路径

        Args:
            install_path: 项目安装路径
            config_path_config: 配置路径配置

        Returns:
            配置文件路径
        """
        if config_path_config and config_path_config.lower() not in [
            "auto",
            "none",
            "null",
            "",
        ]:
            return PathResolver.resolve_path(config_path_config, install_path)

        # 默认为 {install_path}/config
        if install_path:
            config_path = Path(install_path) / "config"
            if config_path.exists():
                return str(config_path)

        return None
