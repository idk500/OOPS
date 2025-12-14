"""
统一检测结果渲染器
按照统一格式渲染所有检测器的结果
"""

import html
from typing import Any, Dict, List

from oops.core.diagnostics import CheckResult, SeverityLevel


class UnifiedDetectionRenderer:
    """统一检测结果渲染器"""

    def __init__(self):
        self.severity_icons = {
            SeverityLevel.INFO: "ℹ️",
            SeverityLevel.WARNING: "⚠️",
            SeverityLevel.ERROR: "❌",
            SeverityLevel.CRITICAL: "🔴",
        }

        self.severity_colors = {
            SeverityLevel.INFO: "var(--info-color)",
            SeverityLevel.WARNING: "var(--warning-color)",
            SeverityLevel.ERROR: "var(--error-color)",
            SeverityLevel.CRITICAL: "var(--critical-color)",
        }

    def render_detection_result(self, result: CheckResult) -> str:
        """
        渲染单个检测结果

        格式要求：
        - 折叠显示，但显示所有通过项
        - 默认显示所有警告/错误项
        """
        # 跳过系统信息检测器（已在系统信息模块显示）
        # hardware_info 现在会在检测结果中显示（用于硬件验证）
        if result.check_name in ["system_info", "system_info_new"]:
            return ""

        # 提取检测项详情
        success_items, warning_items, error_items = self._extract_detection_items(
            result
        )

        # 生成摘要信息
        summary = self._generate_summary(
            result, success_items, warning_items, error_items
        )

        # 生成HTML
        html_content = f"""
        <div class="detection-result {result.severity.value}">
            <div class="detection-header">
                <div class="detection-title">
                    {self.severity_icons[result.severity]} 
                    {self._get_display_name(result.check_name)}
                </div>
                <div class="detection-right">
                    <div class="detection-summary">{summary}</div>
                    <button class="collapse-button" onclick="toggleCollapse('{result.check_name}-details')">
                        ▶ 详细信息
                    </button>
                </div>
            </div>

            <div class="detection-message" style="color: {self.severity_colors[result.severity]};">
                {html.escape(result.message)}
            </div>
        """

        # 默认显示错误和警告项（不通过的部分）
        if error_items or warning_items:
            html_content += '<div class="detection-issues">'

            # 错误项
            if error_items:
                html_content += f"""
                <div class="issue-group error">
                    <h4>❌ 错误项 ({len(error_items)})</h4>
                    <ul>
                """
                for item in error_items:
                    # 处理缩进项
                    if item.startswith("INDENT:"):
                        actual_item = item[7:]
                        html_content += (
                            f'<li class="indent-item">{html.escape(actual_item)}</li>'
                        )
                    else:
                        html_content += f"<li>{html.escape(item)}</li>"
                html_content += "</ul></div>"

            # 警告项
            if warning_items:
                html_content += f"""
                <div class="issue-group warning">
                    <h4>⚠️ 警告项 ({len(warning_items)})</h4>
                    <ul>
                """
                for item in warning_items:
                    # 处理缩进项
                    if item.startswith("INDENT:"):
                        actual_item = item[7:]
                        html_content += (
                            f'<li class="indent-item">{html.escape(actual_item)}</li>'
                        )
                    else:
                        html_content += f"<li>{html.escape(item)}</li>"
                html_content += "</ul></div>"

            html_content += "</div>"

        # 折叠的详细信息 - 包含通过项、详细数据、修复建议
        html_content += f"""
            <div id="{result.check_name}-details" class="collapsible-content" style="display: none;">
                <div class="detection-details">
        """

        # 通过项（在详细信息中显示）
        if success_items:
            html_content += f"""
                <div class="issue-group success">
                    <h4>✅ 通过项 ({len(success_items)})</h4>
                    <ul>
            """
            for item in success_items:
                # 处理缩进项（用于网络检测的子项）
                if item.startswith("INDENT:"):
                    actual_item = item[7:]  # 移除INDENT:前缀
                    html_content += (
                        f'<li class="indent-item">{html.escape(actual_item)}</li>'
                    )
                else:
                    html_content += f"<li>{html.escape(item)}</li>"
            html_content += "</ul></div>"

        # 显示原始详细信息（如果有）
        if result.details and result.check_name != "network_connectivity":
            html_content += self._render_raw_details(result.details, result.check_name)

        # 修复建议
        if result.fix_suggestion:
            html_content += f"""
                <div class="fix-suggestion">
                    <h4>💡 修复建议</h4>
                    <p>{html.escape(result.fix_suggestion)}</p>
                </div>
            """

        html_content += """
                </div>
            </div>
        </div>
        """

        return html_content

    def _extract_detection_items(
        self, result: CheckResult
    ) -> tuple[List[str], List[str], List[str]]:
        """从检测结果中提取成功、警告、错误项"""
        success_items = []
        warning_items = []
        error_items = []

        if not result.details:
            return success_items, warning_items, error_items

        # 处理不同检测器的数据结构
        if result.check_name == "hardware_info":
            # hardware_info 有特殊结构
            issues = result.details.get("issues", [])
            warnings = result.details.get("warnings", [])

            error_items.extend(issues)
            warning_items.extend(warnings)

            # 将硬件信息作为通过项显示 - 分行显示详细信息
            cpu_info = result.details.get("cpu", {})
            if cpu_info:
                success_items.append("CPU信息")
                if cpu_info.get("model"):
                    success_items.append(f"INDENT:型号: {cpu_info['model']}")
                if cpu_info.get("cores_physical") and cpu_info.get("cores_logical"):
                    success_items.append(
                        f"INDENT:核心: {cpu_info['cores_physical']}物理/{cpu_info['cores_logical']}逻辑"
                    )
                if cpu_info.get("freq_current") and cpu_info.get("freq_max"):
                    success_items.append(
                        f"INDENT:频率: {cpu_info['freq_current']}/{cpu_info['freq_max']}"
                    )

            memory_info = result.details.get("memory", {})
            if memory_info:
                success_items.append("内存信息")
                if memory_info.get("total"):
                    success_items.append(f"INDENT:总容量: {memory_info['total']}")
                if memory_info.get("available"):
                    success_items.append(f"INDENT:可用: {memory_info['available']}")
                if memory_info.get("used"):
                    success_items.append(f"INDENT:已使用: {memory_info['used']}")
                if memory_info.get("percent"):
                    success_items.append(f"INDENT:使用率: {memory_info['percent']}")

            gpu_info = result.details.get("gpu")
            if gpu_info:
                success_items.append(f"GPU: {gpu_info}")

            storage_info = result.details.get("storage", {})
            if storage_info:
                success_items.append("存储信息")
                if storage_info.get("current_drive"):
                    success_items.append(
                        f"INDENT:当前盘符: {storage_info['current_drive']}"
                    )
                if storage_info.get("total"):
                    success_items.append(f"INDENT:总容量: {storage_info['total']}")
                if storage_info.get("free"):
                    success_items.append(f"INDENT:可用空间: {storage_info['free']}")
                if storage_info.get("used"):
                    success_items.append(f"INDENT:已使用: {storage_info['used']}")
                if storage_info.get("percent"):
                    success_items.append(f"INDENT:使用率: {storage_info['percent']}")
                if storage_info.get("type"):
                    success_items.append(f"INDENT:类型: {storage_info['type']}")

            display_info = result.details.get("display", {})
            if display_info.get("primary_resolution"):
                # 如果分辨率有问题，它会在error_items中，这里只在没有问题时显示
                if not any("分辨率" in item for item in error_items):
                    success_items.append(
                        f"主显示器分辨率: {display_info['primary_resolution']}"
                    )

        elif result.check_name == "system_settings":
            # system_settings 有特殊结构
            issues = result.details.get("issues", [])
            warnings = result.details.get("warnings", [])
            settings = result.details.get("settings", {})

            error_items.extend(issues)
            warning_items.extend(warnings)

            # 将设置信息作为通过项显示
            for key, value in settings.items():
                if key == "hdr_enabled":
                    status = "启用" if value else "禁用"
                    success_items.append(f"HDR: {status}")
                elif key == "night_light_enabled":
                    status = "启用" if value else "禁用"
                    success_items.append(f"夜间模式: {status}")
                elif key == "color_filter_enabled":
                    status = "启用" if value else "禁用"
                    success_items.append(f"颜色滤镜: {status}")
                elif key == "primary_resolution":
                    success_items.append(f"主显示器分辨率: {value}")

        elif result.check_name == "network_connectivity":
            # 网络检测的特殊处理 - 按类型分组
            type_groups = {
                "git_repo": {"name": "Git仓库", "success": [], "failed": []},
                "pypi_source": {"name": "PyPI源", "success": [], "failed": []},
                "mirror_site": {"name": "镜像站点", "success": [], "failed": []},
                "github_proxy": {"name": "GitHub代理", "success": [], "failed": []},
                "project_website": {"name": "项目官网", "success": [], "failed": []},
                "mihoyo_api": {"name": "米哈游API", "success": [], "failed": []},
            }

            # 分类收集网络检测结果
            for url, detail in result.details.items():
                if isinstance(detail, dict):
                    item_type = detail.get("type", "unknown")
                    item_status = detail.get("status", "unknown")
                    response_time = detail.get("response_time_ms", 0)
                    error_msg = detail.get("error", "")

                    url_display = url.replace("https://", "").replace("http://", "")
                    if len(url_display) > 40:
                        url_display = url_display[:37] + "..."

                    if item_type in type_groups:
                        if item_status == "success":
                            type_groups[item_type]["success"].append(
                                f"{url_display} ({response_time:.0f}ms)"
                            )
                        elif item_status in ["error", "timeout", "failure"]:
                            error_display = (
                                error_msg[:30] + "..."
                                if len(error_msg) > 30
                                else error_msg
                            )
                            type_groups[item_type]["failed"].append(
                                f"{url_display}: {error_display}"
                            )

            # 生成分类摘要 - 使用HTML友好的格式
            for type_key, group_data in type_groups.items():
                success_count = len(group_data["success"])
                failed_count = len(group_data["failed"])
                total_count = success_count + failed_count

                if total_count > 0:
                    type_name = group_data["name"]
                    # 只生成一个摘要，显示成功/总数 可用
                    success_items.append(
                        f"【{type_name}】{success_count}/{total_count} 可用"
                    )

                    # 添加具体的成功项到详细信息
                    for item in group_data["success"]:
                        success_items.append(f"INDENT:{item}")

                    # 添加具体的失败项到详细信息
                    if failed_count > 0:
                        # 只在详细信息中显示失败项，不生成单独的失败摘要
                        for item in group_data["failed"]:
                            error_items.append(f"INDENT:{item}")

        else:
            # 通用处理：遍历details中的所有项
            for key, value in result.details.items():
                if isinstance(value, dict):
                    status = value.get("status", "unknown")
                    message = value.get("message", value.get("error", str(value)))

                    if status == "success":
                        success_items.append(f"{key}: {message}")
                    elif status in ["error", "failure", "timeout"]:
                        error_items.append(f"{key}: {message}")
                    elif status == "warning":
                        warning_items.append(f"{key}: {message}")
                elif isinstance(value, list):
                    # 处理列表类型的数据
                    if key in ["issues", "errors"]:
                        error_items.extend(value)
                    elif key in ["warnings"]:
                        warning_items.extend(value)
                    elif key in ["success", "passed"]:
                        success_items.extend(value)

        return success_items, warning_items, error_items

    def _generate_summary(
        self,
        result: CheckResult,
        success_items: List[str],
        warning_items: List[str],
        error_items: List[str],
    ) -> str:
        """生成检测结果摘要"""
        # 排除INDENT项的计数（这些是子项，不应该计入总数）
        success_count = len(
            [item for item in success_items if not item.startswith("INDENT:")]
        )
        warning_count = len(
            [item for item in warning_items if not item.startswith("INDENT:")]
        )
        error_count = len(
            [item for item in error_items if not item.startswith("INDENT:")]
        )

        total_items = success_count + warning_count + error_count

        if total_items == 0:
            return "无详细项目"

        summary_parts = []
        if success_count > 0:
            summary_parts.append(f"✅ {success_count}项通过")
        if warning_count > 0:
            summary_parts.append(f"⚠️ {warning_count}项警告")
        if error_count > 0:
            summary_parts.append(f"❌ {error_count}项错误")

        return " | ".join(summary_parts)

    def _render_raw_details(self, details: Dict[str, Any], check_name: str = "") -> str:
        """渲染原始详细信息 - 直接显示在详细信息区域"""
        # 项目版本检测的特殊渲染
        if check_name == "project_version":
            return self._render_project_version_details(details)

        html_content = """
        <div class="raw-details">
            <h4>📋 详细数据</h4>
            <div class="details-grid">
        """

        for key, value in details.items():
            if key in ["issues", "warnings", "settings"]:
                continue  # 这些已经在上面处理过了

            display_key = self._get_display_name(key)
            if isinstance(value, dict):
                # 嵌套字典
                html_content += f"""
                <div class="detail-group">
                    <strong>{display_key}:</strong>
                    <ul>
                """
                for sub_key, sub_value in value.items():
                    display_name = self._get_display_name(sub_key)
                    escaped_value = html.escape(str(sub_value))
                    html_content += f"<li>{display_name}: {escaped_value}</li>"
                html_content += "</ul></div>"
            elif isinstance(value, list):
                # 列表
                html_content += f"""
                <div class="detail-group">
                    <strong>{display_key}:</strong>
                    <ul>
                """
                for item in value:
                    html_content += f"<li>{html.escape(str(item))}</li>"
                html_content += "</ul></div>"
            else:
                # 简单值
                html_content += f"""
                <div class="detail-item">
                    <span class="detail-label">{display_key}:</span>
                    <span class="detail-value">{html.escape(str(value))}</span>
                </div>
                """

        html_content += """
            </div>
        </div>
        """

        return html_content

    def _render_project_version_details(self, details: Dict[str, Any]) -> str:
        """渲染项目版本详细信息"""
        html_content = """
        <div class="raw-details">
            <h4>📋 版本详情</h4>
            <div class="details-grid">
        """

        # 渲染本地版本
        version_info = details.get("version", {})
        local_version = version_info.get("local", {})
        remote_version = version_info.get("remote")

        if local_version:
            html_content += """
            <div class="detail-group">
                <strong>📦 本地版本:</strong>
                <ul>
            """
            if local_version.get("is_git_repo"):
                if local_version.get("current_branch"):
                    html_content += (
                        f"<li>分支: {html.escape(local_version['current_branch'])}</li>"
                    )
                if local_version.get("current_commit"):
                    commit = html.escape(local_version["current_commit"])
                    html_content += f"<li>Commit: {commit}</li>"
                if local_version.get("current_tag"):
                    html_content += (
                        f"<li>标签: {html.escape(local_version['current_tag'])}</li>"
                    )
                if local_version.get("last_update"):
                    last_update = html.escape(local_version["last_update"])
                    html_content += f"<li>最后更新: {last_update}</li>"
                if local_version.get("has_uncommitted_changes") is not None:
                    status = "是" if local_version["has_uncommitted_changes"] else "否"
                    html_content += f"<li>未提交更改: {status}</li>"
            else:
                html_content += "<li>不是 Git 仓库</li>"
            html_content += "</ul></div>"

        # 渲染远程版本
        if remote_version:
            html_content += """
            <div class="detail-group">
                <strong>🌐 远程最新版本:</strong>
                <ul>
            """
            if remote_version.get("tag_name"):
                html_content += (
                    f"<li>版本: {html.escape(remote_version['tag_name'])}</li>"
                )
            if remote_version.get("name"):
                html_content += f"<li>名称: {html.escape(remote_version['name'])}</li>"
            if remote_version.get("published_at"):
                html_content += (
                    f"<li>发布时间: {html.escape(remote_version['published_at'])}</li>"
                )
            if remote_version.get("source"):
                source_name = (
                    "Gitee" if remote_version["source"] == "gitee" else "GitHub"
                )
                html_content += f"<li>来源: {source_name}</li>"
            html_content += "</ul></div>"
        else:
            html_content += """
            <div class="detail-group">
                <strong>🌐 远程最新版本:</strong>
                <p style="color: #6b7280;">无法获取（请检查网络连接）</p>
            </div>
            """

        # 渲染启动器版本
        launcher_info = details.get("launcher", {})
        if launcher_info:
            html_content += """
            <div class="detail-group">
                <strong>🚀 启动器版本:</strong>
                <ul>
            """
            if launcher_info.get("exists"):
                if launcher_info.get("version"):
                    html_content += (
                        f"<li>版本: {html.escape(launcher_info['version'])}</li>"
                    )
                if launcher_info.get("file"):
                    html_content += (
                        f"<li>文件: {html.escape(launcher_info['file'])}</li>"
                    )
                if launcher_info.get("error"):
                    error = html.escape(launcher_info["error"])
                    html_content += f"<li style='color: #ef4444;'>错误: {error}</li>"
            else:
                html_content += "<li>未找到启动器版本文件</li>"
                if launcher_info.get("error"):
                    error = html.escape(launcher_info["error"])
                    html_content += f"<li style='color: #ef4444;'>错误: {error}</li>"
            html_content += "</ul></div>"

        html_content += """
            </div>
        </div>
        """

        return html_content

    def _get_display_name(self, key: str) -> str:
        """获取显示名称"""
        display_names = {
            # 检测器名称
            "hardware_info": "硬件信息",
            "system_info_new": "系统信息",
            "system_settings": "系统设置",
            "network_connectivity": "网络连通性",
            "python_environment": "Python环境",
            "environment_dependencies": "环境依赖",
            "path_validation": "路径规范",
            "game_settings": "游戏启动项设置",
            "project_version": "项目版本状态",
            "system_info": "系统信息",
            # 通用字段名
            "status": "状态",
            "message": "消息",
            "error": "错误",
            "warning": "警告",
            "success": "成功",
            "details": "详细信息",
            "settings": "设置",
            "issues": "问题",
            "warnings": "警告",
            "recommendations": "建议",
            # 系统相关
            "hdr_enabled": "HDR状态",
            "night_light_enabled": "夜间模式",
            "color_filter_enabled": "颜色滤镜",
            "primary_resolution": "主显示器分辨率",
            # 网络相关
            "response_time_ms": "响应时间",
            "status_code": "状态码",
            "content_length": "内容长度",
        }

        return display_names.get(key, key.replace("_", " ").title())
