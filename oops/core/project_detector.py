"""
项目检测器
自动检测当前目录是否是项目目录，并生成配置
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectDetector:
    """项目检测器 - 自动识别项目类型"""

    def __init__(self):
        # 项目特征标识
        self.project_signatures = {
            "zenless_zone_zero": {
                "name": "绝区零一条龙",
                "markers": [
                    "zzz_od",
                    "ZenlessZoneZero",
                    "OneDragon-Launcher.exe",
                    "src/zzz_od",
                ],
                "config_files": ["config", ".venv", "requirements.txt"],
            },
            "maa_assistant": {
                "name": "MAA明日方舟助手",
                "markers": [
                    "MAA.exe",
                    "MaaCore.dll",
                    "resource",
                ],
                "config_files": ["config", "cache"],
            },
            "ok_wuthering_waves": {
                "name": "OK鸣潮脚本",
                "markers": [
                    "ok-ww",
                    "wuthering",
                ],
                "config_files": ["config", ".venv"],
            },
        }

    def detect_current_directory(self) -> Optional[Dict[str, Any]]:
        """检测当前目录是否是项目目录

        Returns:
            项目信息字典，如果不是项目目录则返回None
        """
        current_dir = Path.cwd()

        logger.info(f"检测当前目录: {current_dir}")

        # 检查每个项目类型
        for project_id, project_info in self.project_signatures.items():
            if self._match_project(current_dir, project_info):
                return {
                    "project_id": project_id,
                    "project_name": project_info["name"],
                    "install_path": str(current_dir),
                    "detected": True,
                }

        return None

    def _match_project(self, directory: Path, project_info: Dict[str, Any]) -> bool:
        """匹配项目特征"""
        markers = project_info["markers"]
        matched_count = 0

        # 检查标识文件/目录
        for marker in markers:
            marker_path = directory / marker
            if marker_path.exists():
                matched_count += 1
                logger.debug(f"找到标识: {marker}")

        # 至少匹配一个标识才认为是该项目
        return matched_count > 0

    def generate_config_from_detection(
        self, detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据检测结果生成配置

        Args:
            detection_result: 检测结果

        Returns:
            生成的配置字典
        """
        project_id = detection_result["project_id"]
        install_path = detection_result["install_path"]

        # 基础配置模板
        config = {
            "project": {
                "name": detection_result["project_name"],
                "type": "game_script",
                "paths": {
                    "install_path": install_path,
                    "config_path": str(Path(install_path) / "config"),
                },
            },
            "checks": {
                "network": {"enabled": True},
                "environment": {"enabled": True, "project_path": install_path},
                "paths": {"enabled": True},
            },
        }

        # 根据项目类型添加特定配置
        if project_id == "zenless_zone_zero":
            config["checks"]["network"]["git_repos"] = [
                "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git",
                "https://gitee.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git",
            ]
            config["checks"]["network"]["pypi_sources"] = [
                "https://pypi.org/simple/",
                "https://pypi.tuna.tsinghua.edu.cn/simple/",
            ]
            config["checks"]["environment"]["python_version"] = ">=3.8"
            config["checks"]["environment"]["virtual_env"] = True

        return config

    def scan_parent_directories(self, max_depth: int = 3) -> Optional[Dict[str, Any]]:
        """向上扫描父目录寻找项目根目录

        Args:
            max_depth: 最大扫描深度

        Returns:
            项目信息字典，如果未找到则返回None
        """
        current_dir = Path.cwd()

        for i in range(max_depth):
            logger.debug(f"扫描目录 (深度{i}): {current_dir}")

            # 检查当前目录
            for project_id, project_info in self.project_signatures.items():
                if self._match_project(current_dir, project_info):
                    return {
                        "project_id": project_id,
                        "project_name": project_info["name"],
                        "install_path": str(current_dir),
                        "detected": True,
                        "depth": i,
                    }

            # 向上一级
            parent = current_dir.parent
            if parent == current_dir:  # 已到根目录
                break
            current_dir = parent

        return None

    def list_potential_projects(
        self, search_paths: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """列出可能的项目目录

        Args:
            search_paths: 搜索路径列表，默认搜索常见位置

        Returns:
            项目信息列表
        """
        if search_paths is None:
            # 默认搜索路径
            search_paths = [
                "D:\\",
                "E:\\",
                "C:\\Games",
                str(Path.home() / "Documents"),
            ]

        found_projects = []

        for search_path in search_paths:
            search_dir = Path(search_path)
            if not search_dir.exists():
                continue

            try:
                # 只搜索第一层子目录
                for item in search_dir.iterdir():
                    if item.is_dir():
                        for project_id, project_info in self.project_signatures.items():
                            if self._match_project(item, project_info):
                                found_projects.append(
                                    {
                                        "project_id": project_id,
                                        "project_name": project_info["name"],
                                        "install_path": str(item),
                                        "detected": True,
                                    }
                                )
                                break
            except PermissionError:
                logger.debug(f"无权限访问: {search_dir}")
                continue

        return found_projects


def auto_detect_and_configure() -> Optional[Dict[str, Any]]:
    """自动检测并配置

    Returns:
        配置字典，如果未检测到项目则返回None
    """
    detector = ProjectDetector()

    # 1. 检测当前目录
    detection = detector.detect_current_directory()
    if detection:
        logger.info(f"✅ 检测到项目: {detection['project_name']}")
        return detector.generate_config_from_detection(detection)

    # 2. 扫描父目录
    detection = detector.scan_parent_directories()
    if detection:
        logger.info(
            f"✅ 在父目录检测到项目: {detection['project_name']} (深度: {detection['depth']})"
        )
        return detector.generate_config_from_detection(detection)

    # 3. 未检测到项目
    logger.info("未检测到项目，使用默认配置")
    return None
