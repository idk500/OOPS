"""
默认配置加载器
提供默认配置的加载和合并功能
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

logger = logging.getLogger(__name__)


class DefaultConfigLoader:
    """默认配置加载器"""

    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.defaults_file = self.config_dir / "defaults.yaml"
        self._defaults = None

    def load_defaults(self) -> Dict[str, Any]:
        """加载默认配置"""
        if self._defaults is None:
            if self.defaults_file.exists():
                try:
                    with open(self.defaults_file, "r", encoding="utf-8") as f:
                        self._defaults = yaml.safe_load(f) or {}
                    logger.info(f"已加载默认配置: {self.defaults_file}")
                except Exception as e:
                    logger.warning(f"加载默认配置失败: {e}，使用内置默认配置")
                    self._defaults = self._create_builtin_defaults()
            else:
                logger.info("默认配置文件不存在，使用内置默认配置")
                self._defaults = self._create_builtin_defaults()
        return self._defaults

    def _create_builtin_defaults(self) -> Dict[str, Any]:
        """创建内置默认配置（如果文件不存在）"""
        return {
            "network_defaults": {
                "git_repos": [
                    {
                        "url": "https://github.com",
                        "name": "GitHub",
                        "type": "git_repo",
                    }
                ],
                "pypi_sources": [
                    {
                        "url": "https://pypi.org/simple/",
                        "name": "PyPI官方",
                        "type": "pypi_source",
                    },
                    {
                        "url": "https://pypi.tuna.tsinghua.edu.cn/simple/",
                        "name": "清华镜像",
                        "type": "pypi_source",
                    },
                ],
            }
        }

    def get_network_defaults(self) -> Dict[str, Any]:
        """获取网络检测默认配置"""
        defaults = self.load_defaults()
        return defaults.get("network_defaults", {})

    def merge_network_config(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和项目配置

        合并规则：
        1. git_repos: 默认 + 项目特定（追加）
        2. pypi_sources: 项目配置优先，否则使用默认
        3. 其他配置: 项目配置优先，否则使用默认
        4. disable_defaults: 可以禁用默认配置中的某些类型

        Args:
            project_config: 项目配置字典

        Returns:
            合并后的网络配置
        """
        defaults = self.get_network_defaults()
        project_network = project_config.get("checks", {}).get("network", {})

        # 如果网络检测未启用，返回空配置
        if not project_network.get("enabled", False):
            return {}

        merged = {}

        # 处理禁用列表
        disable_list = project_network.get("disable_defaults", [])

        # Git仓库：追加项目特定的仓库
        if "git_repos" not in disable_list:
            default_repos = defaults.get("git_repos", [])
            project_repos = self._normalize_url_list(
                project_network.get("git_repos", []), "git_repo"
            )
            merged["git_repos"] = default_repos + project_repos
        else:
            # 禁用默认，只使用项目配置
            merged["git_repos"] = self._normalize_url_list(
                project_network.get("git_repos", []), "git_repo"
            )

        # PyPI源：项目配置优先，否则使用默认
        if "pypi_sources" not in disable_list:
            project_pypi = project_network.get("pypi_sources")
            if project_pypi is not None:
                # 项目有配置，使用项目配置
                merged["pypi_sources"] = self._normalize_url_list(
                    project_pypi, "pypi_source"
                )
            else:
                # 项目无配置，使用默认
                merged["pypi_sources"] = defaults.get("pypi_sources", [])
        else:
            # 禁用默认，只使用项目配置
            merged["pypi_sources"] = self._normalize_url_list(
                project_network.get("pypi_sources", []), "pypi_source"
            )

        # 其他配置项：项目配置优先，否则使用默认
        for key in [
            "mirror_sites",
            "github_proxies",
            "project_websites",
            "mihoyo_apis",
        ]:
            if key not in disable_list:
                project_value = project_network.get(key)
                if project_value is not None:
                    merged[key] = self._normalize_url_list(
                        project_value, key.rstrip("s")
                    )
                else:
                    merged[key] = defaults.get(key, [])
            else:
                # 禁用默认，只使用项目配置
                merged[key] = self._normalize_url_list(
                    project_network.get(key, []), key.rstrip("s")
                )

        return merged

    def _normalize_url_list(
        self, url_list: List[Any], default_type: str
    ) -> List[Dict[str, str]]:
        """标准化URL列表

        支持两种格式：
        1. 简单字符串列表: ["https://example.com"]
        2. 字典列表: [{"url": "https://example.com", "name": "Example", "type": "..."}]

        Args:
            url_list: URL列表
            default_type: 默认类型

        Returns:
            标准化后的字典列表
        """
        if not url_list:
            return []

        normalized = []
        for item in url_list:
            if isinstance(item, str):
                # 简单字符串格式
                normalized.append(
                    {
                        "url": item,
                        "name": self._extract_domain(item),
                        "type": default_type,
                    }
                )
            elif isinstance(item, dict):
                # 字典格式，确保有必需的字段
                url = item.get("url", "")
                normalized.append(
                    {
                        "url": url,
                        "name": item.get("name", self._extract_domain(url)),
                        "type": item.get("type", default_type),
                    }
                )
        return normalized

    def _extract_domain(self, url: str) -> str:
        """从URL提取域名作为默认名称"""
        try:
            # 移除协议
            if "://" in url:
                url = url.split("://", 1)[1]
            # 提取域名
            domain = url.split("/")[0]
            return domain
        except:
            return url
