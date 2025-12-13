"""
网络连通性检测器
检测Git仓库、PyPI源、镜像源、项目官网等网络连接状态
"""

import asyncio
import logging
import re
import time
from typing import Any, Dict, List, Optional

import aiohttp

from oops.core.config import DetectionRule
from oops.core.default_config import DefaultConfigLoader

logger = logging.getLogger(__name__)


class GhProxyUpdater:
    """GitHub 代理地址动态更新器"""

    PROXY_JS_URL = "https://ghproxy.link/js/src_views_home_HomeView_vue.js"

    @classmethod
    async def fetch_latest_proxy(cls) -> Optional[str]:
        """从 ghproxy.link 获取最新的代理地址"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    cls.PROXY_JS_URL, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        return None

                    js_content = await response.text()

                    # 使用正则表达式提取代理 URL
                    pattern = r"<a\s+href=\\\\\"(https://[^\"\\\\]+)\\\\\".*?target="
                    match = re.search(pattern, js_content)
                    if match:
                        proxy_url = match.group(1)
                        # 验证 URL 格式
                        if re.match(
                            r"^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", proxy_url
                        ):
                            return proxy_url

                    return None
        except Exception as e:
            logger.warning(f"获取动态代理地址失败: {e}")
            return None


class NetworkConnectivityDetector(DetectionRule):
    """网络连通性检测器"""

    def __init__(self):
        super().__init__(
            name="network_connectivity",
            description="检测网络连通性",
            severity="warning",
        )
        self.timeout = 10  # 默认超时时间10秒
        self.default_loader = DefaultConfigLoader()

    async def check_async(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """异步执行网络检测"""
        # 检查配置
        config_result = self._check_config(config)
        if config_result:
            return config_result

        # 合并默认配置和项目配置
        merged_config = self.default_loader.merge_network_config(config)

        # 创建检测任务
        tasks = await self._create_detection_tasks(merged_config)

        # 执行任务并处理结果
        results = await self._execute_tasks(tasks)

        # 分析整体网络状态
        overall_status = self._analyze_network_status(results)

        # 生成详细消息
        message = self._generate_message(results)

        return {"status": overall_status, "message": message, "details": results}

    def _check_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查配置是否启用和有效"""
        network_config = config.get("checks", {}).get("network", {})
        if not network_config.get("enabled", False):
            return {"status": "skipped", "message": "网络检测已禁用"}
        return None

    async def _create_detection_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建所有检测任务"""
        tasks = []

        # Git仓库检测任务
        tasks.extend(await self._create_git_repo_tasks(merged_config))

        # PyPI源检测任务
        tasks.extend(await self._create_pypi_source_tasks(merged_config))

        # 镜像源检测任务
        tasks.extend(await self._create_mirror_site_tasks(merged_config))

        # 项目官网检测任务
        tasks.extend(await self._create_project_website_tasks(merged_config))

        # GitHub代理检测任务
        tasks.extend(await self._create_github_proxy_tasks(merged_config))

        # 米哈游API检测任务
        tasks.extend(await self._create_mihoyo_api_tasks(merged_config))

        return tasks

    async def _create_git_repo_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建Git仓库检测任务"""
        tasks = []
        git_repos = merged_config.get("git_repos", [])
        for repo_item in git_repos:
            repo_url = (
                repo_item.get("url") if isinstance(repo_item, dict) else repo_item
            )
            # Git检测暂时不支持代理控制
            task = self._check_git_repo(repo_url)
            tasks.append(task)
        return tasks

    async def _create_pypi_source_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建PyPI源检测任务"""
        tasks = []
        pypi_sources = merged_config.get("pypi_sources", [])
        for source_item in pypi_sources:
            source_url = (
                source_item.get("url") if isinstance(source_item, dict) else source_item
            )
            # 创建两个任务：一个使用代理，一个不使用代理
            tasks.append(self._check_pypi_source(source_url, use_proxy=True))
            tasks.append(self._check_pypi_source(source_url, use_proxy=False))
        return tasks

    async def _create_mirror_site_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建镜像源检测任务"""
        tasks = []
        mirror_sites = merged_config.get("mirror_sites", [])
        for mirror_item in mirror_sites:
            mirror_url = (
                mirror_item.get("url") if isinstance(mirror_item, dict) else mirror_item
            )
            # 创建两个任务：一个使用代理，一个不使用代理
            tasks.append(self._check_mirror_site(mirror_url, use_proxy=True))
            tasks.append(self._check_mirror_site(mirror_url, use_proxy=False))
        return tasks

    async def _create_project_website_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建项目官网检测任务"""
        tasks = []
        project_websites = merged_config.get("project_websites", [])
        for website_item in project_websites:
            website_url = (
                website_item.get("url")
                if isinstance(website_item, dict)
                else website_item
            )
            # 创建两个任务：一个使用代理，一个不使用代理
            tasks.append(self._check_website(website_url, use_proxy=True))
            tasks.append(self._check_website(website_url, use_proxy=False))
        return tasks

    async def _create_github_proxy_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建GitHub代理检测任务"""
        tasks = []
        github_proxies = merged_config.get("github_proxies", [])

        # 处理动态代理
        github_proxies = await self._process_dynamic_proxies(github_proxies)

        # 为每个代理创建检测任务
        for proxy_item in github_proxies:
            proxy_url = self._get_proxy_url(proxy_item)
            tasks.extend(self._create_proxy_detection_tasks(proxy_url))

        return tasks

    async def _process_dynamic_proxies(self, github_proxies: List[Any]) -> List[Any]:
        """处理动态代理配置"""
        dynamic_proxies = self._get_dynamic_proxies(github_proxies)

        if dynamic_proxies:
            latest_proxy = await GhProxyUpdater.fetch_latest_proxy()
            if latest_proxy:
                # 将动态获取的代理添加到检测列表
                return [
                    {"url": latest_proxy, "name": "动态代理", "type": "github_proxy"}
                ] + self._filter_out_dynamic_proxies(github_proxies)
            else:
                # 动态获取代理失败，过滤掉原始的dynamic代理
                return self._filter_out_dynamic_proxies(github_proxies)

        return github_proxies

    def _get_dynamic_proxies(self, github_proxies: List[Any]) -> List[Any]:
        """获取动态代理配置"""
        return [p for p in github_proxies if isinstance(p, dict) and p.get("dynamic")]

    def _filter_out_dynamic_proxies(self, github_proxies: List[Any]) -> List[Any]:
        """过滤掉动态代理配置"""
        return [
            p for p in github_proxies if not (isinstance(p, dict) and p.get("dynamic"))
        ]

    def _get_proxy_url(self, proxy_item: Any) -> str:
        """获取代理URL"""
        if isinstance(proxy_item, dict):
            return proxy_item.get("url", "")
        return proxy_item

    def _create_proxy_detection_tasks(self, proxy_url: str) -> List[asyncio.Task]:
        """为单个代理创建检测任务"""
        # 创建两个任务：一个使用代理，一个不使用代理
        return [
            self._check_github_proxy(proxy_url, use_proxy=True),
            self._check_github_proxy(proxy_url, use_proxy=False),
        ]

    async def _create_mihoyo_api_tasks(
        self, merged_config: Dict[str, Any]
    ) -> List[asyncio.Task]:
        """创建米哈游API检测任务"""
        tasks = []
        mihoyo_api = merged_config.get("mihoyo_api", [])
        for api_item in mihoyo_api:
            api_url = api_item.get("url") if isinstance(api_item, dict) else api_item
            # 创建两个任务：一个使用代理，一个不使用代理
            tasks.append(self._check_website(api_url, use_proxy=True))
            tasks.append(self._check_website(api_url, use_proxy=False))
        return tasks

    async def _execute_tasks(self, tasks: List[asyncio.Task]) -> Dict[str, Any]:
        """并行执行任务并处理结果"""
        results = {}

        if tasks:
            check_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(check_results):
                if isinstance(result, Exception):
                    logger.error(f"网络检测失败: {result}")
                    results[f"check_{i}"] = {"status": "error", "error": str(result)}
                else:
                    results.update(result)

        return results

    def _generate_message(self, results: Dict[str, Any]) -> str:
        """生成检测结果消息"""
        message_parts = [f"网络检测完成，共检测 {len(results)} 个目标"]

        # 按类型统计
        type_stats = {}
        for result in results.values():
            result_type = result.get("type", "unknown")
            if result_type not in type_stats:
                type_stats[result_type] = {"success": 0, "failed": 0, "total": 0}

            type_stats[result_type]["total"] += 1
            if result.get("status") == "success":
                type_stats[result_type]["success"] += 1
            else:
                type_stats[result_type]["failed"] += 1

        # 添加分组统计信息
        type_names = {
            "git_repo": "Git仓库",
            "pypi_source": "PyPI源",
            "github_proxy": "GitHub代理",
            "mihoyo_api": "米哈游API",
            "mirror_site": "镜像站点",
            "project_website": "项目官网",
        }

        # 关键组和可选组
        critical_types = ["git_repo", "pypi_source"]

        for type_key, stats in type_stats.items():
            type_name = type_names.get(type_key, type_key)
            is_critical = type_key in critical_types

            if stats["failed"] > 0:
                if stats["success"] > 0:
                    # 部分失败
                    if is_critical:
                        message_parts.append(
                            f"{type_name}: {stats['success']}/{stats['total']} 可用 ✓"
                        )
                    else:
                        message_parts.append(
                            f"{type_name}: {stats['success']}/{stats['total']} 可用 "
                            f"(建议避免使用失败的{stats['failed']}个)"
                        )
                else:
                    # 全部失败
                    if is_critical:
                        message_parts.append(
                            f"{type_name}: ❌ 全部失败 ({stats['total']}个)"
                        )
                    else:
                        message_parts.append(
                            f"{type_name}: ⚠️ 全部失败 ({stats['total']}个，可选)"
                        )

        return "\n".join(message_parts)

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """同步执行网络检测（包装异步方法）"""
        try:
            return asyncio.run(self.check_async(config))
        except Exception as e:
            logger.error(f"网络检测执行失败: {e}")
            return {
                "status": "error",
                "message": f"网络检测执行失败: {str(e)}",
                "details": {},
            }

    async def _check_git_repo(self, repo_url: str) -> Dict[str, Any]:
        """检测Git仓库连通性"""
        start_time = time.time()
        try:
            # 使用git ls-remote检测仓库可访问性
            process = await asyncio.create_subprocess_exec(
                "git",
                "ls-remote",
                repo_url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )

            response_time = (time.time() - start_time) * 1000  # 毫秒

            if process.returncode == 0:
                return {
                    repo_url: {
                        "status": "success",
                        "response_time_ms": response_time,
                        "type": "git_repo",
                    }
                }
            else:
                return {
                    repo_url: {
                        "status": "failure",
                        "error": stderr.decode("utf-8", errors="ignore").strip(),
                        "response_time_ms": response_time,
                        "type": "git_repo",
                    }
                }

        except asyncio.TimeoutError:
            return {
                repo_url: {
                    "status": "timeout",
                    "error": f"检测超时 ({self.timeout}秒)",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "git_repo",
                }
            }
        except Exception as e:
            return {
                repo_url: {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "git_repo",
                }
            }

    async def _check_pypi_source(
        self, source_url: str, use_proxy: bool = False
    ) -> Dict[str, Any]:
        """检测PyPI源连通性"""
        start_time = time.time()
        try:
            # 构造PyPI简单API请求
            if not source_url.endswith("/"):
                source_url += "/"
            test_url = f"{source_url}pip/"

            # 创建客户端会话配置
            session_kwargs = {}
            if use_proxy:
                # 使用系统代理
                session_kwargs["trust_env"] = True
            else:
                # 不使用代理
                session_kwargs["trust_env"] = False
                session_kwargs["connector"] = aiohttp.TCPConnector(force_close=True)

            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.get(
                    test_url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    key = (
                        f"{source_url}_(proxy)"
                        if use_proxy
                        else f"{source_url}_(direct)"
                    )
                    if response.status == 200:
                        content_length = response.headers.get("Content-Length", 0)
                        return {
                            key: {
                                "status": "success",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "content_length": int(content_length),
                                "type": "pypi_source",
                                "proxy": use_proxy,
                            }
                        }
                    else:
                        return {
                            key: {
                                "status": "failure",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "type": "pypi_source",
                                "proxy": use_proxy,
                            }
                        }

        except asyncio.TimeoutError:
            key = f"{source_url}_(proxy)" if use_proxy else f"{source_url}_(direct)"
            return {
                key: {
                    "status": "timeout",
                    "error": f"请求超时 ({self.timeout}秒)",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "pypi_source",
                    "proxy": use_proxy,
                }
            }
        except Exception as e:
            key = f"{source_url}_(proxy)" if use_proxy else f"{source_url}_(direct)"
            return {
                key: {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "pypi_source",
                    "proxy": use_proxy,
                }
            }

    async def _check_mirror_site(
        self, mirror_url: str, use_proxy: bool = False
    ) -> Dict[str, Any]:
        """检测镜像站点连通性"""
        start_time = time.time()
        try:
            # 创建客户端会话配置
            session_kwargs = {}
            if use_proxy:
                # 使用系统代理
                session_kwargs["trust_env"] = True
            else:
                # 不使用代理
                session_kwargs["trust_env"] = False
                session_kwargs["connector"] = aiohttp.TCPConnector(force_close=True)

            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.get(
                    mirror_url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    key = (
                        f"{mirror_url}_(proxy)"
                        if use_proxy
                        else f"{mirror_url}_(direct)"
                    )
                    if response.status == 200:
                        content_length = response.headers.get("Content-Length", 0)
                        return {
                            key: {
                                "status": "success",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "content_length": int(content_length),
                                "type": "mirror_site",
                                "proxy": use_proxy,
                            }
                        }
                    else:
                        return {
                            key: {
                                "status": "failure",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "type": "mirror_site",
                                "proxy": use_proxy,
                            }
                        }

        except asyncio.TimeoutError:
            key = f"{mirror_url}_(proxy)" if use_proxy else f"{mirror_url}_(direct)"
            return {
                key: {
                    "status": "timeout",
                    "error": f"请求超时 ({self.timeout}秒)",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "mirror_site",
                    "proxy": use_proxy,
                }
            }
        except Exception as e:
            key = f"{mirror_url}_(proxy)" if use_proxy else f"{mirror_url}_(direct)"
            return {
                key: {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "mirror_site",
                    "proxy": use_proxy,
                }
            }

    async def _check_website(
        self, website_url: str, use_proxy: bool = False
    ) -> Dict[str, Any]:
        """检测项目官网连通性"""
        start_time = time.time()
        try:
            # 创建客户端会话配置
            session_kwargs = {}
            if use_proxy:
                # 使用系统代理
                session_kwargs["trust_env"] = True
            else:
                # 不使用代理
                session_kwargs["trust_env"] = False
                session_kwargs["connector"] = aiohttp.TCPConnector(force_close=True)

            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.get(
                    website_url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    key = (
                        f"{website_url}_(proxy)"
                        if use_proxy
                        else f"{website_url}_(direct)"
                    )
                    if response.status == 200:
                        content_length = response.headers.get("Content-Length", 0)
                        return {
                            key: {
                                "status": "success",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "content_length": int(content_length),
                                "type": "project_website",
                                "proxy": use_proxy,
                            }
                        }
                    else:
                        return {
                            key: {
                                "status": "failure",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "type": "project_website",
                                "proxy": use_proxy,
                            }
                        }

        except asyncio.TimeoutError:
            key = f"{website_url}_(proxy)" if use_proxy else f"{website_url}_(direct)"
            return {
                key: {
                    "status": "timeout",
                    "error": f"请求超时 ({self.timeout}秒)",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "project_website",
                    "proxy": use_proxy,
                }
            }
        except Exception as e:
            key = f"{website_url}_(proxy)" if use_proxy else f"{website_url}_(direct)"
            return {
                key: {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "project_website",
                    "proxy": use_proxy,
                }
            }

    async def _check_github_proxy(
        self, proxy_url: str, use_proxy: bool = False
    ) -> Dict[str, Any]:
        """检测GitHub代理连通性"""
        start_time = time.time()
        try:
            # 创建客户端会话配置
            session_kwargs = {}
            if use_proxy:
                # 使用系统代理
                session_kwargs["trust_env"] = True
            else:
                # 不使用代理
                session_kwargs["trust_env"] = False
                session_kwargs["connector"] = aiohttp.TCPConnector(force_close=True)

            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.get(
                    proxy_url, timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000

                    key = (
                        f"{proxy_url}_(proxy)" if use_proxy else f"{proxy_url}_(direct)"
                    )
                    if response.status == 200:
                        return {
                            key: {
                                "status": "success",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "type": "github_proxy",
                                "proxy": use_proxy,
                            }
                        }
                    else:
                        return {
                            key: {
                                "status": "failure",
                                "response_time_ms": response_time,
                                "status_code": response.status,
                                "type": "github_proxy",
                                "proxy": use_proxy,
                            }
                        }

        except asyncio.TimeoutError:
            key = f"{proxy_url}_(proxy)" if use_proxy else f"{proxy_url}_(direct)"
            return {
                key: {
                    "status": "timeout",
                    "error": f"请求超时 ({self.timeout}秒)",
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "github_proxy",
                    "proxy": use_proxy,
                }
            }
        except Exception as e:
            key = f"{proxy_url}_(proxy)" if use_proxy else f"{proxy_url}_(direct)"
            return {
                key: {
                    "status": "error",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000,
                    "type": "github_proxy",
                    "proxy": use_proxy,
                }
            }

    def _analyze_network_status(self, results: Dict[str, Any]) -> str:
        """分析整体网络状态

        分组逻辑：
        - Git仓库：至少一个可用即可
        - PyPI源：至少一个可用即可
        - GitHub代理：至少一个可用即可（可选）
        - 米哈游API：至少一个可用即可（可选）
        """
        if not results:
            return "unknown"

        groups = self._group_results_by_type_for_analysis(results)

        # 检查关键组（必须至少有一个可用）
        if self._has_critical_issue(groups):
            return "error"

        # 检查可选组（全部失败才警告）
        if self._has_warning_issue(groups):
            return "warning"

        return "success"

    def _group_results_by_type_for_analysis(
        self, results: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按类型分组结果用于分析"""
        groups = {
            "git_repo": [],
            "pypi_source": [],
            "github_proxy": [],
            "mirror_site": [],
            "project_website": [],
        }

        for url, result in results.items():
            result_type = result.get("type", "unknown")
            groups[result_type].append(result)

        return groups

    def _has_critical_issue(self, groups: Dict[str, List[Dict[str, Any]]]) -> bool:
        """检查关键组是否有问题"""
        critical_groups = ["git_repo", "pypi_source"]

        for group_name in critical_groups:
            group_results = groups[group_name]
            if group_results and not self._has_any_success(group_results):
                return True

        return False

    def _has_warning_issue(self, groups: Dict[str, List[Dict[str, Any]]]) -> bool:
        """检查可选组是否有问题"""
        optional_groups = [
            "github_proxy",
            "mirror_site",
            "project_website",
        ]

        for group_name in optional_groups:
            group_results = groups[group_name]
            if group_results and self._has_all_failed(group_results):
                return True

        return False

    def _has_any_success(self, results: List[Dict[str, Any]]) -> bool:
        """检查是否至少有一个成功结果"""
        return any(r.get("status") == "success" for r in results)

    def _has_all_failed(self, results: List[Dict[str, Any]]) -> bool:
        """检查是否全部失败"""
        return all(r.get("status") in ["failure", "timeout", "error"] for r in results)

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取网络问题修复建议"""
        status = result.get("status", "unknown")

        # 如果状态正常，返回空字符串（不显示建议）
        if status == "success":
            return ""

        details = result.get("details", {})
        groups = self._group_results_by_type(details)
        suggestions = []

        # 获取各类型的修复建议
        suggestions.extend(self._get_git_repo_suggestion(groups))
        suggestions.extend(self._get_pypi_source_suggestion(groups))
        suggestions.extend(self._get_github_proxy_suggestion(groups))

        if suggestions:
            return "; ".join(suggestions)

        # 通用建议
        if status == "warning":
            return "部分网络连接存在问题，建议使用可用的源"
        elif status == "error":
            return "网络连接存在严重问题，请检查网络连接、防火墙设置或DNS配置"
        else:
            return "网络状态未知，建议检查网络连接"

    def _group_results_by_type(self, details: Dict[str, Any]) -> Dict[str, List[tuple]]:
        """按类型分组结果"""
        groups = {
            "git_repo": [],
            "pypi_source": [],
            "github_proxy": [],
        }

        for url, detail in details.items():
            result_type = detail.get("type", "unknown")
            if result_type in groups:
                groups[result_type].append((url, detail))

        return groups

    def _get_git_repo_suggestion(self, groups: Dict[str, List[tuple]]) -> List[str]:
        """获取Git仓库修复建议"""
        git_failed = [
            url for url, d in groups["git_repo"] if d.get("status") != "success"
        ]
        git_success = [
            url for url, d in groups["git_repo"] if d.get("status") == "success"
        ]

        suggestions = []
        if git_failed and git_success:
            suggestions.append(f"Git仓库: 建议使用可用的源 ({len(git_success)}个可用)")
        elif git_failed and not git_success:
            suggestions.append("Git仓库: 全部失败，请检查网络连接或使用代理")
        return suggestions

    def _get_pypi_source_suggestion(self, groups: Dict[str, List[tuple]]) -> List[str]:
        """获取PyPI源修复建议"""
        pypi_failed = [
            url for url, d in groups["pypi_source"] if d.get("status") != "success"
        ]
        pypi_success = [
            url for url, d in groups["pypi_source"] if d.get("status") == "success"
        ]

        suggestions = []
        if pypi_failed and pypi_success:
            suggestions.append(f"PyPI源: 建议使用可用的源 ({len(pypi_success)}个可用)")
        elif pypi_failed and not pypi_success:
            suggestions.append("PyPI源: 全部失败，请检查网络连接或更换镜像源")
        return suggestions

    def _get_github_proxy_suggestion(self, groups: Dict[str, List[tuple]]) -> List[str]:
        """获取GitHub代理修复建议"""
        proxy_failed, proxy_success = self._get_proxy_status_lists(groups)
        return self._generate_proxy_suggestions(proxy_failed, proxy_success)

    def _get_proxy_status_lists(
        self, groups: Dict[str, List[tuple]]
    ) -> tuple[List[str], List[str]]:
        """获取代理失败和成功的URL列表"""
        proxy_failed = [
            url for url, d in groups["github_proxy"] if d.get("status") != "success"
        ]
        proxy_success = [
            url for url, d in groups["github_proxy"] if d.get("status") == "success"
        ]
        return proxy_failed, proxy_success

    def _generate_proxy_suggestions(
        self, proxy_failed: List[str], proxy_success: List[str]
    ) -> List[str]:
        """根据代理状态生成建议"""
        suggestions = []
        if proxy_failed and proxy_success:
            self._add_partial_failure_suggestions(proxy_failed, suggestions)
        elif proxy_failed and not proxy_success and len(proxy_failed) > 0:
            self._add_total_failure_suggestions(suggestions)
        return suggestions

    def _add_partial_failure_suggestions(
        self, proxy_failed: List[str], suggestions: List[str]
    ) -> None:
        """添加部分失败的建议"""
        failed_domains = self._extract_unique_failed_domains(proxy_failed[:2])
        if failed_domains:
            suggestions.append(f"GitHub代理: 避免使用 {', '.join(failed_domains)}")

    def _add_total_failure_suggestions(self, suggestions: List[str]) -> None:
        """添加全部失败的建议"""
        suggestions.append("GitHub代理: 全部失败，建议直连或使用其他代理")

    def _extract_unique_failed_domains(self, proxy_failed: List[str]) -> List[str]:
        """从失败的代理URL中提取唯一域名"""
        failed_domains = []
        for url in proxy_failed:
            domain = self._extract_domain_safely(url)
            if domain and domain != "dynamic":
                failed_domains.append(domain)
        return list(set(failed_domains))

    def _extract_domain_safely(self, url: str) -> Optional[str]:
        """安全地从URL中提取域名"""
        try:
            # 跳过任何包含"dynamic"的URL
            if "dynamic" in url.lower():
                return None

            # 提取域名部分，处理各种URL格式
            if "//" in url:
                return url.split("//")[1].split("/")[0]
            elif "_" in url:
                # 处理格式 like "domain_(proxy)"
                return url.split("_")[0]
            else:
                return url
        except Exception:
            # 跳过异常情况，避免显示无意义的内容
            return None
