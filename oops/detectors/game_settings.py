"""
游戏设置检测器
检测游戏安装路径和配置文件
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class GameSettingsDetector(DetectionRule):
    """游戏设置检测器 - 检测游戏路径配置"""

    def __init__(self):
        super().__init__(
            name="game_settings",
            description="游戏设置检测",
            severity="error",
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行游戏设置检测"""
        try:
            game_config = config.get("checks", {}).get("game_settings", {})
            if not game_config.get("enabled", False):
                return {"status": "skipped", "message": "游戏设置检测未启用"}

            project_path = (
                config.get("project", {}).get("paths", {}).get("install_path", "")
            )
            if not project_path:
                return {"status": "skipped", "message": "未配置项目路径"}

            # 收集检测信息
            detection_info = {
                "config_file": self._check_config_file(project_path, game_config),
                "game_executable": self._check_game_executable(
                    project_path, game_config
                ),
                "default_path": self._check_default_path(game_config),
            }

            # 分析问题
            issues = []
            warnings = []
            recommendations = []

            # 检查配置文件
            config_check = detection_info["config_file"]
            if not config_check.get("exists"):
                warnings.append("游戏配置文件不存在")
                recommendations.append(
                    f"请确保配置文件存在: {config_check.get('path', '未知路径')}"
                )

            # 检查游戏可执行文件
            game_check = detection_info["game_executable"]
            if config_check.get("exists"):
                if not game_check.get("exists"):
                    issues.append("游戏可执行文件不存在")
                    game_path = game_check.get("path", "未配置")
                    recommendations.append(f"请检查游戏路径配置: {game_path}")
                    recommendations.append(
                        "确保游戏已正确安装，或更新配置文件中的游戏路径"
                    )

            # 检查默认路径（仅作为信息提示）
            default_check = detection_info["default_path"]
            if not default_check.get("exists"):
                # 默认路径不存在不算问题，只是提示
                pass

            # 确定状态
            if issues:
                status = "error"
                message = f"游戏设置存在 {len(issues)} 个问题"
            elif warnings:
                status = "warning"
                message = f"游戏设置存在 {len(warnings)} 个警告"
            else:
                status = "success"
                message = "游戏设置检查通过"

            return {
                "status": status,
                "message": message,
                "details": {
                    "detection": detection_info,
                    "issues": issues,
                    "warnings": warnings,
                    "recommendations": recommendations,
                },
            }
        except Exception as e:
            logger.error(f"游戏设置检测失败: {e}")
            return {"status": "error", "message": f"游戏设置检测失败: {str(e)}"}

    def _check_config_file(
        self, project_path: str, game_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查游戏配置文件"""
        try:
            config_file = game_config.get("config_file", "config/01/game_account.yml")
            config_path = Path(project_path) / config_file

            exists = config_path.exists()

            result = {
                "exists": exists,
                "path": str(config_path),
            }

            if exists:
                # 尝试读取配置
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)
                        result["config_data"] = config_data
                        result["readable"] = True
                except Exception as e:
                    logger.debug(f"读取配置文件失败: {e}")
                    result["readable"] = False
                    result["error"] = str(e)
            else:
                result["readable"] = False

            return result
        except Exception as e:
            logger.error(f"检查配置文件失败: {e}")
            return {"exists": False, "error": str(e)}

    def _check_game_executable(
        self, project_path: str, game_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查游戏可执行文件"""
        try:
            # 先检查配置文件
            config_check = self._check_config_file(project_path, game_config)

            if not config_check.get("exists") or not config_check.get("readable"):
                return {
                    "exists": False,
                    "path": "配置文件不存在或无法读取",
                    "source": "config_file",
                }

            config_data = config_check.get("config_data", {})

            # 优先使用 local_game_path，其次使用 game_path
            game_path = config_data.get("local_game_path") or config_data.get(
                "game_path"
            )

            if not game_path:
                return {
                    "exists": False,
                    "path": "配置文件中未找到游戏路径",
                    "source": "config_file",
                }

            # 检查文件是否存在
            game_exe = Path(game_path)
            exists = game_exe.exists() and game_exe.is_file()

            return {
                "exists": exists,
                "path": str(game_path),
                "source": (
                    "local_game_path"
                    if "local_game_path" in config_data
                    else "game_path"
                ),
            }
        except Exception as e:
            logger.error(f"检查游戏可执行文件失败: {e}")
            return {"exists": False, "error": str(e)}

    def _check_default_path(self, game_config: Dict[str, Any]) -> Dict[str, Any]:
        """检查默认游戏路径"""
        try:
            default_path = game_config.get(
                "default_game_path",
                r"C:\Program Files\miHoYo Launcher\games\ZenlessZoneZero Game\ZenlessZoneZero.exe",
            )

            if not default_path:
                return {"exists": False, "path": "未配置默认路径"}

            default_exe = Path(default_path)
            exists = default_exe.exists() and default_exe.is_file()

            return {
                "exists": exists,
                "path": str(default_path),
            }
        except Exception as e:
            logger.error(f"检查默认路径失败: {e}")
            return {"exists": False, "error": str(e)}

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        details = result.get("details", {})
        recommendations = details.get("recommendations", [])
        return "; ".join(recommendations) if recommendations else ""
