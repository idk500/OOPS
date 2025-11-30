"""
HTML 渲染器模块
从数据模型生成 HTML 报告，实现数据和渲染的完全分离
"""

import html
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from oops.core.brief_report import BriefReportGenerator
from oops.core.data_models import DiagnosticReport, SystemInfoData
from oops.core.diagnostics import CheckResult, SeverityLevel
from oops.core.report_modules import ReportModuleManager
from oops.core.styles import ReportStyles


class HTMLRenderer:
    """HTML 渲染器 - 从数据模型生成 HTML"""

    def __init__(
        self, include_details: bool = True, include_fix_suggestions: bool = True
    ):
        self.styles = ReportStyles.get_full_stylesheet()
        self.scripts = self._get_scripts()
        self.include_details = include_details
        self.include_fix_suggestions = include_fix_suggestions

    def render(self, report: DiagnosticReport) -> str:
        """渲染完整的 HTML 报告"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OOPS 诊断报告 - {html.escape(report.project_name)}</title>
    <style>{self.styles}</style>
</head>
<body>
    <div class="container">
        {self._render_header(report)}
        {self._render_summary(report.summary)}
        {self._render_system_info(report.system_info)}
        {self._render_check_results(report.check_results)}
        {self._render_issues(report.issues)}
    </div>
    <script>{self.scripts}</script>
</body>
</html>"""

    def _render_header(self, report: DiagnosticReport) -> str:
        """渲染页头"""
        from oops import __version__

        return f"""
        <div class="header">
            <h1>🔍 OOPS 运行预检报告 - {html.escape(report.project_name)}</h1>
            <p style="color: var(--info-color); margin-bottom: 15px;">开源一键问题排查器 | 版本: {__version__} | 生成时间: {html.escape(report.timestamp)}</p>
            <div class="project-info">
                <p><strong>项目路径:</strong> {html.escape(report.project_path)}</p>
                <p><strong>运行路径:</strong> {html.escape(report.current_path)}</p>
            </div>
        </div>
        """

    def _render_summary(self, summary: Dict[str, Any]) -> str:
        """渲染摘要卡片"""
        return f"""
        <div class="section">
            <h2 class="section-title">📊 检测摘要</h2>
            <div class="summary-stats">
                <span>总检测项: {summary.get('total', 0)}</span>
                <span>成功完成: {summary.get('completed', 0)}</span>
                <span>执行失败: {summary.get('failed', 0)}</span>
                <span>关键问题: {summary.get('critical_issues', 0)}</span>
                <span>警告: {summary.get('warning_issues', 0)}</span>
                <span>成功率: {summary.get('success_rate', 0):.1f}%</span>
            </div>
        </div>
        """

    def _render_system_info(self, system_info: Dict[str, Any]) -> str:
        """渲染系统信息"""
        if not system_info:
            return ""

        system_data = SystemInfoData(**system_info)
        summary = system_data.get_summary()

        return f"""
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">🖥️ 系统信息</h2>
                <button class="collapse-button" onclick="toggleCollapse('system-info-content')">
                    ▶ 展开详情
                </button>
            </div>
            <p style="color: #6b7280; margin: 10px 0;">{summary}</p>
            <div id="system-info-content" class="collapsible-content">
                {self._render_system_details(system_data)}
            </div>
        </div>
        """

    def _render_system_details(self, system_data: SystemInfoData) -> str:
        """渲染系统详细信息"""
        html_parts = ['<div class="system-info-grid">']

        # 基本信息
        if system_data.basic:
            html_parts.append(
                '<div class="info-group"><h3>基本信息</h3><div class="info-items">'
            )
            for key, value in system_data.basic.items():
                display_name = self._get_display_name(key)
                html_parts.append(
                    f"""
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                """
                )
            html_parts.append("</div></div>")

        # 硬件信息
        if system_data.hardware:
            html_parts.append(
                '<div class="info-group"><h3>硬件信息</h3><div class="info-items">'
            )

            # CPU信息 - 分行显示
            if "cpu" in system_data.hardware:
                cpu_info = system_data.hardware["cpu"]
                if isinstance(cpu_info, dict):
                    # 型号
                    if cpu_info.get("model"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">CPU型号:</span>
                    <span class="info-value">{html.escape(str(cpu_info['model']))}</span>
                </div>
                """
                        )
                    # 核心
                    if cpu_info.get("cores_physical") and cpu_info.get("cores_logical"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">CPU核心:</span>
                    <span class="info-value">{cpu_info['cores_physical']}物理/{cpu_info['cores_logical']}逻辑</span>
                </div>
                """
                        )
                    # 频率
                    if cpu_info.get("freq_current") and cpu_info.get("freq_max"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">CPU频率:</span>
                    <span class="info-value">{cpu_info['freq_current']}/{cpu_info['freq_max']}</span>
                </div>
                """
                        )
                else:
                    # 兼容旧格式
                    html_parts.append(
                        f"""
                <div class="info-item">
                    <span class="info-label">CPU:</span>
                    <span class="info-value">{html.escape(str(cpu_info))}</span>
                </div>
                """
                    )

            # 内存信息 - 分行显示
            if "memory" in system_data.hardware:
                memory_info = system_data.hardware["memory"]
                if isinstance(memory_info, dict):
                    # 总容量
                    if memory_info.get("total"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">内存总容量:</span>
                    <span class="info-value">{html.escape(str(memory_info['total']))}</span>
                </div>
                """
                        )
                    # 可用
                    if memory_info.get("available"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">内存可用:</span>
                    <span class="info-value">{html.escape(str(memory_info['available']))}</span>
                </div>
                """
                        )
                    # 已用
                    if memory_info.get("used"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">内存已用:</span>
                    <span class="info-value">{html.escape(str(memory_info['used']))}</span>
                </div>
                """
                        )
                    # 使用率
                    if memory_info.get("percent"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">内存使用率:</span>
                    <span class="info-value">{html.escape(str(memory_info['percent']))}%</span>
                </div>
                """
                        )
                else:
                    # 兼容旧格式
                    html_parts.append(
                        f"""
                <div class="info-item">
                    <span class="info-label">内存:</span>
                    <span class="info-value">{html.escape(str(memory_info))}</span>
                </div>
                """
                    )

            # GPU信息
            if "gpu" in system_data.hardware:
                gpu_info = system_data.hardware["gpu"]
                html_parts.append(
                    f"""
                <div class="info-item">
                    <span class="info-label">GPU:</span>
                    <span class="info-value">{html.escape(str(gpu_info))}</span>
                </div>
                """
                )

            # 磁盘信息 - 分行显示
            if "storage" in system_data.hardware:
                storage_info = system_data.hardware["storage"]
                if isinstance(storage_info, dict):
                    # 当前盘符
                    if storage_info.get("current_drive"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">当前盘符:</span>
                    <span class="info-value">{html.escape(str(storage_info['current_drive']))}</span>
                </div>
                """
                        )
                    # 总容量
                    if storage_info.get("total"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">磁盘总容量:</span>
                    <span class="info-value">{html.escape(str(storage_info['total']))}</span>
                </div>
                """
                        )
                    # 可用空间
                    if storage_info.get("free"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">磁盘可用空间:</span>
                    <span class="info-value">{html.escape(str(storage_info['free']))}</span>
                </div>
                """
                        )
                    # 已使用
                    if storage_info.get("used"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">磁盘已使用:</span>
                    <span class="info-value">{html.escape(str(storage_info['used']))}</span>
                </div>
                """
                        )
                    # 使用率
                    if storage_info.get("percent"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">磁盘使用率:</span>
                    <span class="info-value">{html.escape(str(storage_info['percent']))}%</span>
                </div>
                """
                        )
                    # 类型
                    if storage_info.get("type"):
                        html_parts.append(
                            f"""
                <div class="info-item">
                    <span class="info-label">磁盘类型:</span>
                    <span class="info-value">{html.escape(str(storage_info['type']))}</span>
                </div>
                """
                        )
                else:
                    # 兼容旧格式
                    html_parts.append(
                        f"""
                <div class="info-item">
                    <span class="info-label">磁盘:</span>
                    <span class="info-value">{html.escape(str(storage_info))}</span>
                </div>
                """
                    )

            # 其他硬件信息
            for key, value in system_data.hardware.items():
                if key not in ["cpu", "memory", "gpu", "storage"]:
                    display_name = self._get_display_name(key)
                    html_parts.append(
                        f"""
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                """
                    )

            html_parts.append("</div></div>")

        # 存储信息
        if system_data.storage:
            html_parts.append(
                '<div class="info-group"><h3>存储信息</h3><div class="info-items">'
            )
            for key, value in system_data.storage.items():
                display_name = self._get_display_name(key)
                html_parts.append(
                    f"""
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                """
                )
            html_parts.append("</div></div>")

        html_parts.append("</div>")
        return "".join(html_parts)

    def _render_check_results(self, check_results: Dict[str, Any]) -> str:
        """渲染检测结果"""
        if not check_results:
            return ""

        html_parts = ['<div class="section"><h2 class="section-title">🔍 检测结果</h2>']

        for check_name, result in check_results.items():
            severity = result.get("severity", "info")
            status = result.get("status", "unknown")
            message = result.get("message", "")

            html_parts.append(
                f"""
            <div class="check-item {severity}">
                <div class="check-header">
                    <div class="check-name">{html.escape(check_name)}</div>
                    <span class="check-status status-{status}">{status}</span>
                </div>
                <div class="check-message">{html.escape(message)}</div>
            </div>
            """
            )

        html_parts.append("</div>")
        return "".join(html_parts)

    def _render_issues(self, issues: Dict[str, Any]) -> str:
        """渲染问题列表"""
        total_issues = (
            len(issues.get("critical", []))
            + len(issues.get("errors", []))
            + len(issues.get("warnings", []))
        )

        if total_issues == 0:
            return ""

        html_parts = [
            f'<div class="section"><h2 class="section-title">⚠️ 发现的问题 ({total_issues})</h2>'
        ]

        # 关键问题
        if issues.get("critical"):
            html_parts.append(
                '<h3 style="color: var(--critical-color);">🔴 关键问题</h3>'
            )
            for issue in issues["critical"]:
                html_parts.append(
                    f"""
                <div class="issue-item critical">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                """
                )

        # 错误
        if issues.get("errors"):
            html_parts.append('<h3 style="color: var(--error-color);">❌ 错误</h3>')
            for issue in issues["errors"]:
                html_parts.append(
                    f"""
                <div class="issue-item error">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                """
                )

        # 警告
        if issues.get("warnings"):
            html_parts.append('<h3 style="color: var(--warning-color);">⚠️ 警告</h3>')
            for issue in issues["warnings"]:
                html_parts.append(
                    f"""
                <div class="issue-item warning">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                """
                )

        html_parts.append("</div>")
        return "".join(html_parts)

    def _get_display_name(self, key: str) -> str:
        """获取字段的显示名称"""
        name_map = {
            "os": "操作系统",
            "os_version": "系统版本",
            "os_release": "系统发行版",
            "architecture": "架构",
            "machine": "机器类型",
            "processor": "处理器",
            "python_version": "Python版本",
            "python_executable": "Python路径",
            "current_path": "当前路径",
            "cpu_cores_physical": "物理核心数",
            "cpu_cores_logical": "逻辑核心数",
            "cpu_freq_current": "当前频率",
            "cpu_freq_max": "最大频率",
            "cpu_model": "CPU型号",
            "memory_total": "总内存",
            "memory_available": "可用内存",
            "memory_used": "已用内存",
            "memory_percent": "内存使用率",
            "gpu_info": "显卡信息",
            "current_drive": "当前驱动器",
            "disk_total": "磁盘总容量",
            "disk_used": "已用空间",
            "disk_free": "可用空间",
            "disk_usage_percent": "磁盘使用率",
            "disk_type": "磁盘类型",
        }
        return name_map.get(key, key)

    def _get_html_footer(self) -> str:
        """获取HTML页脚模板"""
        return """
        </div>
    </body>
</html>"""

    def _get_html_title_section(self, project_name: str) -> str:
        """获取HTML标题部分"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <div class="header">
            <h1>🚀 OOPS 运行预检报告 - {html.escape(project_name)}</h1>
            <p style="color: #6b7280; margin: 5px 0;">让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly</p>
            <div class="timestamp">生成时间: {timestamp}</div>
        </div>"""


    def _get_html_summary_section(self, summary: Dict[str, Any]) -> str:
        """获取HTML摘要部分"""
        success_rate = summary.get("success_rate", 0)
        return f"""
        <div class="section">
            <h2 class="section-title">📊 检测摘要</h2>
            <div class="summary-stats">
                <span>总检测项: {summary.get('total_checks', 0)}</span>
                <span>成功完成: {summary.get('completed', 0)}</span>
                <span>执行失败: {summary.get('failed', 0)}</span>
                <span>关键问题: {summary.get('critical_issues', 0)}</span>
                <span>错误问题: {summary.get('error_issues', 0)}</span>
                <span>警告问题: {summary.get('warning_issues', 0)}</span>
                <span>成功率: {success_rate:.1f}%</span>
            </div>
        </div>"""

    def _get_html_critical_issues_section(
        self, critical_results: List[CheckResult]
    ) -> str:
        """获取HTML关键问题部分"""
        content = """
        <div class="section">
            <h2 class="section-title">🚨 关键问题</h2>"""

        for result in critical_results:
            content += self._get_html_check_item(result)

        content += "\n        </div>"
        return content

    def _get_html_detailed_results_section(self, results: List[CheckResult]) -> str:
        """获取HTML详细结果部分"""
        content = """
        <div class="section">
            <h2 class="section-title">🔍 详细检测结果</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                以下是每个检测项的详细信息，包括具体的失败项和警告项。
            </p>"""

        # 按严重程度排序：critical > error > warning > info
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.ERROR: 1,
            SeverityLevel.WARNING: 2,
            SeverityLevel.INFO: 3,
        }

        sorted_results = sorted(
            results, key=lambda r: severity_order.get(r.severity, 4)
        )

        for result in sorted_results:
            content += self._get_html_check_item(result)

        content += "\n        </div>"
        return content

    def _get_html_check_item(self, result: CheckResult) -> str:
        """获取HTML检测项模板"""
        status_class = f"status-{result.status.value}"
        severity_class = f"check-item {result.severity.value}"

        # 提取详细信息中的失败项
        details_html = ""
        if result.details:
            failed_items = []
            warning_items = []
            success_items = []

            # 处理特殊的检测器数据结构
            if result.check_name == "system_settings":
                # system_settings 有特殊的数据结构
                issues = result.details.get("issues", [])
                warnings = result.details.get("warnings", [])
                settings = result.details.get("settings", {})

                # 添加错误项
                for issue in issues:
                    failed_items.append(f"<li>{html.escape(issue)}</li>")

                # 添加警告项
                for warning in warnings:
                    warning_items.append(f"<li>{html.escape(warning)}</li>")

                # 显示检测的设置项
                if settings:
                    settings_info = []
                    for setting_key, setting_value in settings.items():
                        if setting_key == "hdr_enabled":
                            status = "启用" if setting_value else "禁用"
                            settings_info.append(f"HDR: {status}")
                        elif setting_key == "night_light_enabled":
                            status = "启用" if setting_value else "禁用"
                            settings_info.append(f"夜间模式: {status}")
                        elif setting_key == "color_filter_enabled":
                            status = "启用" if setting_value else "禁用"
                            settings_info.append(f"颜色滤镜: {status}")
                        elif setting_key == "primary_resolution":
                            settings_info.append(f"主显示器分辨率: {setting_value}")

                    if settings_info:
                        success_items.extend(
                            [f"<li>{info}</li>" for info in settings_info]
                        )
            elif result.check_name == "environment_dependencies":
                # environment_dependencies 有嵌套的数据结构
                for key, value in result.details.items():
                    if isinstance(value, dict):
                        item_status = value.get("status", "unknown")
                        item_message = value.get("message", "")

                        # 特殊处理 project_dependencies
                        if key == "project_dependencies" and "details" in value:
                            proj_details = value.get("details", {})

                            # Git 工具检测
                            if "git" in proj_details:
                                git_info = proj_details["git"]
                                git_status = git_info.get("status", "unknown")
                                git_msg = git_info.get("message", "")

                                if git_status == "success":
                                    git_details = git_info.get("details", {})
                                    git_version = git_details.get(
                                        "git_version", "未知版本"
                                    )
                                    success_items.append(
                                        f"<li><strong>Git 工具</strong>: ✅ {html.escape(git_msg)} ({html.escape(git_version)})</li>"
                                    )
                                elif git_status == "warning":
                                    warning_items.append(
                                        f"<li><strong>Git 工具</strong>: {html.escape(git_msg)}</li>"
                                    )
                                elif git_status == "error":
                                    failed_items.append(
                                        f"<li><strong>Git 工具</strong>: {html.escape(git_msg)}</li>"
                                    )

                            # 嵌入式 Python 检测
                            if "embedded_python" in proj_details:
                                py_info = proj_details["embedded_python"]
                                py_status = py_info.get("status", "unknown")
                                py_msg = py_info.get("message", "")

                                if py_status == "success":
                                    success_items.append(
                                        f"<li><strong>嵌入式 Python</strong>: ✅ {html.escape(py_msg)}</li>"
                                    )
                                elif py_status == "warning":
                                    warning_items.append(
                                        f"<li><strong>嵌入式 Python</strong>: {html.escape(py_msg)}</li>"
                                    )
                        else:
                            # 其他标准项
                            if item_status == "error":
                                failed_items.append(
                                    f"<li><strong>{html.escape(key)}</strong>: {html.escape(item_message)}</li>"
                                )
                            elif item_status == "warning":
                                warning_items.append(
                                    f"<li><strong>{html.escape(key)}</strong>: {html.escape(item_message)}</li>"
                                )
                            elif item_status == "success":
                                success_items.append(
                                    f"<li><strong>{html.escape(key)}</strong>: ✅ {html.escape(item_message)}</li>"
                                )
            else:
                # 处理其他检测器的标准数据结构
                for key, value in result.details.items():
                    if isinstance(value, dict):
                        item_status = value.get("status", "unknown")
                        item_message = value.get("message", value.get("error", ""))

                        if item_status in ["error", "failure", "timeout"]:
                            failed_items.append(
                                f"<li><strong>{html.escape(key)}</strong>: {html.escape(item_message)}</li>"
                            )
                        elif item_status == "warning":
                            warning_items.append(
                                f"<li><strong>{html.escape(key)}</strong>: {html.escape(item_message)}</li>"
                            )
                        elif item_status == "success":
                            success_items.append(
                                f"<li><strong>{html.escape(key)}</strong>: ✅ {html.escape(item_message)}</li>"
                            )

            if failed_items or warning_items:
                details_html = "<div class='check-details-list'>"

                if failed_items:
                    details_html += (
                        "<div class='failed-items'><strong>❌ 失败项:</strong><ul>"
                    )
                    details_html += "".join(failed_items)
                    details_html += "</ul></div>"

                if warning_items:
                    details_html += (
                        "<div class='warning-items'><strong>⚠️ 警告项:</strong><ul>"
                    )
                    details_html += "".join(warning_items)
                    details_html += "</ul></div>"

                if success_items and len(success_items) <= 5:  # 只显示少量成功项
                    details_html += (
                        "<div class='success-items'><strong>✅ 通过项:</strong><ul>"
                    )
                    details_html += "".join(success_items)
                    details_html += "</ul></div>"

                details_html += "</div>"

        fix_suggestion_html = ""
        if result.fix_suggestion and self.include_fix_suggestions:
            fix_suggestion_html = f"""
                <div class="fix-suggestion">
                    <strong>💡 修复建议:</strong> {html.escape(result.fix_suggestion)}
                </div>"""

        return f"""
            <div class="{severity_class}">
                <div class="check-header">
                    <div class="check-name">{html.escape(result.check_name)}</div>
                    <div class="check-status {status_class}">{result.status.value.upper()}</div>
                </div>
                <div class="check-message">{html.escape(result.message)}</div>
                {details_html}
                <div class="check-meta">
                    <small>执行时间: {result.execution_time:.2f}s | 严重程度: {result.severity.value}</small>
                </div>
                {fix_suggestion_html}
            </div>"""

    def _get_html_fix_suggestions_section(self, results: List[CheckResult]) -> str:
        """获取HTML修复建议部分"""
        fix_suggestions = self._extract_fix_suggestions(results)

        content = """
        <div class="section">
            <h2 class="section-title">🛠️ 修复建议汇总</h2>"""

        for category, suggestions in fix_suggestions.items():
            if suggestions:
                content += f"""
            <div class="check-item info">
                <div class="check-header">
                    <div class="check-name">{html.escape(category)}</div>
                </div>"""

                for suggestion in suggestions:
                    content += f"""
                <div class="check-message">• {html.escape(suggestion)}</div>"""

                content += "\n            </div>"

        content += "\n        </div>"
        return content

    def _extract_fix_suggestions(
        self, results: List[CheckResult]
    ) -> Dict[str, List[str]]:
        """提取修复建议并按类别分组"""
        suggestions = {
            "网络问题": [],
            "环境依赖": [],
            "路径规范": [],
            "系统配置": [],
            "其他问题": [],
        }

        for result in results:
            if result.fix_suggestion and result.severity in [
                SeverityLevel.CRITICAL,
                SeverityLevel.ERROR,
                SeverityLevel.WARNING,
            ]:
                # 简单的关键词分类
                suggestion = result.fix_suggestion
                check_name = result.check_name.lower()

                if any(
                    keyword in check_name
                    for keyword in ["network", "git", "pypi", "mirror"]
                ):
                    suggestions["网络问题"].append(suggestion)
                elif any(
                    keyword in check_name
                    for keyword in ["environment", "python", "dependency", "library"]
                ):
                    suggestions["环境依赖"].append(suggestion)
                elif any(
                    keyword in check_name
                    for keyword in ["path", "directory", "permission"]
                ):
                    suggestions["路径规范"].append(suggestion)
                elif any(
                    keyword in check_name for keyword in ["system", "config", "setting"]
                ):
                    suggestions["系统配置"].append(suggestion)
                else:
                    suggestions["其他问题"].append(suggestion)

        # 去重
        for category in suggestions:
            suggestions[category] = list(set(suggestions[category]))

        return suggestions

    def _get_scripts(self) -> str:
        """获取 JavaScript 脚本"""
        return """
        // 折叠/展开功能
        function toggleCollapse(id) {
            const element = document.getElementById(id);
            const button = event.target;
            if (element.style.display === 'none' || element.style.display === '') {
                element.style.display = 'block';
                button.textContent = '▼ 收起详情';
            } else {
                element.style.display = 'none';
                button.textContent = '▶ 展开详情';
            }
        }
        
        // 复制简报到剪贴板
        function copyBriefText(index) {
            if (typeof window.briefTexts === 'undefined' || !window.briefTexts[index]) {
                alert('简报数据未加载');
                return;
            }
            const text = window.briefTexts[index];
            navigator.clipboard.writeText(text).then(() => {
                alert('简报已复制到剪贴板！');
            }).catch(err => {
                console.error('复制失败:', err);
                // 降级方案：使用 textarea
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                alert('简报已复制到剪贴板！');
            });
        }
        
        // 显示/隐藏 YAML 路径
        function toggleYamlPath() {
            const yamlPath = document.getElementById('yaml-path-display');
            if (yamlPath) {
                if (yamlPath.style.display === 'none' || yamlPath.style.display === '') {
                    yamlPath.style.display = 'block';
                } else {
                    yamlPath.style.display = 'none';
                }
            }
        }

        // 复制 YAML 路径到剪贴板
        function copyYamlPath() {
            const yamlPath = document.querySelector('#yaml-path-display code');
            if (yamlPath) {
                const text = yamlPath.textContent;
                navigator.clipboard.writeText(text).then(() => {
                    alert('YAML 报告路径已复制到剪贴板！');
                }).catch(err => {
                    console.error('复制失败:', err);
                    // 降级方案：使用 textarea
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    alert('YAML 报告路径已复制到剪贴板！');
                });
            }
        }
        """

    def render_full_report(
        self,
        results: List[CheckResult],
        project_name: str,
        summary: Dict[str, Any],
        system_info: Dict[str, Any],
        oops_version: str,
        brief_texts: List[str],
        yaml_path: str = "",
        project_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        渲染完整的HTML报告

        Args:
            results: 检测结果列表
            project_name: 项目名称
            summary: 摘要信息
            system_info: 系统信息
            oops_version: OOPS版本
            brief_texts: 简报文本列表
            yaml_path: YAML报告路径（可选）
            project_config: 项目配置（可选）
        """
        # 获取正确的项目显示名称
        display_project_name = BriefReportGenerator._shorten_project_name(
            project_name, project_config
        )

        # 构建报告内容
        content_parts = []

        # 头部（包含样式和脚本）
        brief_texts_json = json.dumps(brief_texts, ensure_ascii=False)
        header = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OOPS 运行预检报告 - {html.escape(display_project_name)}</title>
    <style>{self.styles}</style>
    <script>
        // 预注入简报数据
        window.briefTexts = {brief_texts_json};
        {self.scripts}
    </script>
</head>
<body>
    <div class="container">
"""
        content_parts.append(header)

        # 标题和项目信息（包含复制简报按钮和YAML路径）
        content_parts.append(
            self._get_html_title_section_with_brief_buttons(
                display_project_name, brief_texts, oops_version, yaml_path
            )
        )

        # 使用模块化系统生成报告内容
        module_manager = ReportModuleManager()
        report_data = {
            "system_info": system_info,
            "summary": summary,
            "results": results,
        }

        # 生成模块化内容
        content_parts.append(module_manager.generate_html_report(report_data))

        # 关键问题（如果有）
        critical_results = [r for r in results if r.severity == SeverityLevel.CRITICAL]
        if critical_results and self.include_details:
            content_parts.append(
                self._get_html_critical_issues_section(critical_results)
            )

        # 修复建议汇总
        if self.include_fix_suggestions:
            content_parts.append(self._get_html_fix_suggestions_section(results))

        # 底部
        content_parts.append(self._get_html_footer())

        return "\n".join(content_parts)

    def _get_html_title_section_with_brief_buttons(
        self,
        project_name: str,
        brief_texts: list,
        oops_version: str,
        yaml_path: str = "",
    ) -> str:
        """获取HTML标题部分（包含复制简报按钮和YAML路径）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 生成简报复制按钮
        brief_buttons = []
        for i, _ in enumerate(brief_texts):
            if len(brief_texts) == 1:
                btn_text = "📋 复制简报"
            else:
                btn_text = f"📋 复制简报 {i + 1}"
            brief_buttons.append(
                f'<button class="action-button" onclick="copyBriefText({i})">{btn_text}</button>'
            )

        # 添加显示YAML路径按钮
        if yaml_path:
            brief_buttons.append(
                '<button class="action-button" onclick="toggleYamlPath()">📄 显示YAML报告路径</button>'
            )

        brief_buttons_html = " ".join(brief_buttons)

        # YAML路径显示区域
        yaml_path_html = ""
        if yaml_path:
            yaml_path_html = f"""
            <div id="yaml-path-display" class="yaml-path-display">
                <strong>📄 YAML报告路径:</strong><br>
                <div style="display: flex; align-items: center; gap: 10px; margin: 5px 0;">
                    <code style="flex: 1; font-family: 'Consolas', 'Monaco', monospace; background: #f3f4f6; padding: 4px 8px; border-radius: 4px; word-break: break-all;">{html.escape(yaml_path)}</code>
                    <button class="action-button" style="padding: 4px 8px; font-size: 12px;" onclick="copyYamlPath()">📋 复制</button>
                </div>
                <small style="color: #6b7280;">💡 将此文件提交给项目开发者以获取支持</small>
            </div>
            """

        return f"""
        <div class="header">
            <h1>🚀 OOPS 运行预检报告 - {html.escape(project_name)}</h1>
            <p style="color: #6b7280; margin: 5px 0;">让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly | 版本: {html.escape(oops_version)} | 生成时间: {timestamp}</p>
            <div class="action-buttons" style="margin-top: 10px;">
                {brief_buttons_html}
            </div>
            {yaml_path_html}
        </div>
        """
