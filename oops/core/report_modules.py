"""
报告模块化组件
将报告生成拆分为独立的模块
"""

import html
from typing import Dict, List, Any
from oops.core.diagnostics import CheckResult, SeverityLevel


class ReportModule:
    """报告模块基类"""

    def __init__(self, name: str, title: str):
        self.name = name
        self.title = title

    def generate_html(self, data: Any) -> str:
        """生成HTML内容"""
        raise NotImplementedError

    def generate_json(self, data: Any) -> Dict[str, Any]:
        """生成JSON内容"""
        raise NotImplementedError


class SystemInfoModule(ReportModule):
    """系统信息模块"""

    def __init__(self):
        super().__init__("system_info", "🖥️ 系统信息")

    def generate_html(self, system_info: Dict[str, Any]) -> str:
        """生成系统信息HTML"""
        # 检查是否有实际数据
        has_data = bool(
            system_info.get("basic") or 
            system_info.get("hardware") or 
            system_info.get("storage") or
            system_info.get("validation")
        )
        
        if not has_data:
            return f"""
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">{self.title}</h2>
                </div>
                <p style="color: #6b7280; margin: 10px 0;">
                    系统信息收集失败或未执行
                </p>
            </div>
            """
        
        # 生成紧凑摘要
        summary_parts = []
        hardware = system_info.get("hardware", {})
        storage = system_info.get("storage", {})
        basic = system_info.get("basic", {})

        if hardware.get("cpu_model"):
            summary_parts.append(f"CPU: {hardware['cpu_model']}")
        if hardware.get("memory_total"):
            summary_parts.append(f"内存: {hardware['memory_total']}")
        if storage.get("disk_type"):
            disk_icon = "⚠️" if storage["disk_type"] == "HDD" else "✅"
            summary_parts.append(f"磁盘: {storage['disk_type']} {disk_icon}")
        if basic.get("os"):
            summary_parts.append(f"系统: {basic['os']}")

        summary_text = " | ".join(summary_parts) if summary_parts else "查看详细信息"

        html_content = f"""
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">{self.title}</h2>
                <button class="collapse-button" onclick="toggleCollapse('system-info-content')">
                    ▶ 展开详情
                </button>
            </div>
            <p style="color: #6b7280; margin: 10px 0;">
                {summary_text}
            </p>
            <div id="system-info-content" class="collapsible-content">
                <div class="system-info-grid">
        """

        # 基本信息（排除显示设置相关）
        basic_info = system_info.get("basic", {})
        display_setting_keys = [
            "hdr_enabled",
            "night_light_enabled",
            "nvidia_filter_enabled",
            "color_filter_enabled",
            "primary_resolution",
        ]

        if basic_info:
            # 过滤出非显示设置的基本信息
            filtered_basic = {
                k: v for k, v in basic_info.items() if k not in display_setting_keys
            }

            if filtered_basic:
                html_content += """
                    <div class="info-group">
                        <h3>基本信息</h3>
                        <div class="info-items">
                """
                for key, value in filtered_basic.items():
                    display_name = self._get_display_name(key)
                    html_content += f"""
                            <div class="info-item">
                                <span class="info-label">{display_name}:</span>
                                <span class="info-value">{html.escape(str(value))}</span>
                            </div>
                    """
                html_content += """
                        </div>
                    </div>
                """

            # 显示设置单独分类
            display_settings = {
                k: v for k, v in basic_info.items() if k in display_setting_keys
            }
            if display_settings:
                html_content += """
                    <div class="info-group">
                        <h3>显示设置</h3>
                        <div class="info-items">
                """
                for key, value in display_settings.items():
                    display_name = self._get_display_name(key)

                    # 分辨率特殊处理（不显示图标，只显示值）
                    if key == "primary_resolution":
                        html_content += f"""
                            <div class="info-item">
                                <span class="info-label">{display_name}:</span>
                                <span class="info-value">{html.escape(str(value))}</span>
                            </div>
                        """
                    else:
                        # 其他显示设置根据布尔值显示图标
                        if value is True:
                            icon = "⚠️"
                            color = "var(--warning-color)"
                        elif value is False:
                            icon = "✅"
                            color = "var(--success-color)"
                        else:
                            icon = "❓"
                            color = "var(--info-color)"

                        html_content += f"""
                            <div class="info-item">
                                <span class="info-label">{display_name}:</span>
                                <span class="info-value" style="color: {color};">
                                    {html.escape(str(value))} {icon}
                                </span>
                            </div>
                        """
                html_content += """
                        </div>
                    </div>
                """

        # 硬件信息
        hardware_info = system_info.get("hardware", {})
        if hardware_info:
            html_content += """
                <div class="info-group">
                    <h3>硬件信息</h3>
                    <div class="info-items">
            """
            for key, value in hardware_info.items():
                display_name = self._get_display_name(key)
                html_content += f"""
                        <div class="info-item">
                            <span class="info-label">{display_name}:</span>
                            <span class="info-value">{html.escape(str(value))}</span>
                        </div>
                """
            html_content += """
                    </div>
                </div>
            """

        # 存储信息
        storage_info = system_info.get("storage", {})
        if storage_info:
            html_content += """
                <div class="info-group">
                    <h3>存储信息</h3>
                    <div class="info-items">
            """
            for key, value in storage_info.items():
                display_name = self._get_display_name(key)
                # 磁盘类型特殊处理，如果是HDD显示警告
                if key == "disk_type" and value == "HDD":
                    html_content += f"""
                        <div class="info-item">
                            <span class="info-label">{display_name}:</span>
                            <span class="info-value" style="color: var(--warning-color);">
                                {html.escape(str(value))} ⚠️
                            </span>
                        </div>
                    """
                else:
                    html_content += f"""
                        <div class="info-item">
                            <span class="info-label">{display_name}:</span>
                            <span class="info-value">{html.escape(str(value))}</span>
                        </div>
                    """
            html_content += """
                    </div>
                </div>
            """

        # 硬件适配结果
        validation = system_info.get("validation", {})
        if validation:
            # 分类收集验证项
            error_items = []
            warning_items = []
            success_items = []

            # 内存验证
            if "memory" in validation:
                mem_val = validation["memory"]
                item_html = f"""
                        <div class="info-item">
                            <span class="info-label">内存验证:</span>
                            <span class="info-value">{{icon}} {html.escape(mem_val.get('message', ''))}</span>
                        </div>
                """
                if mem_val.get("recommendation"):
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--info-color); font-size: 0.9em;">
                                💡 {html.escape(mem_val.get('recommendation'))}
                            </span>
                        </div>
                    """

                if mem_val.get("valid"):
                    success_items.append(item_html.format(icon="✅"))
                else:
                    error_items.append(item_html.format(icon="❌"))

            # 磁盘类型验证
            if "disk_type" in validation:
                disk_val = validation["disk_type"]
                if disk_val.get("warning"):
                    status_icon = "⚠️"
                    color = "var(--warning-color)"
                else:
                    status_icon = "✅"
                    color = "var(--success-color)"

                item_html = f"""
                        <div class="info-item">
                            <span class="info-label">磁盘类型:</span>
                            <span class="info-value" style="color: {color};">
                                {status_icon} {html.escape(disk_val.get('message', ''))}
                            </span>
                        </div>
                """
                if disk_val.get("recommendation"):
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--warning-color); font-size: 0.9em;">
                                💡 {html.escape(disk_val.get('recommendation'))}
                            </span>
                        </div>
                    """

                if disk_val.get("warning"):
                    warning_items.append(item_html)
                else:
                    success_items.append(item_html)

            # 用户名验证（只在有问题时显示）
            if "username" in validation:
                user_val = validation["username"]
                status_icon = "❌" if not user_val.get("valid") else "⚠️"
                color = (
                    "var(--error-color)"
                    if not user_val.get("valid")
                    else "var(--warning-color)"
                )

                item_html = f"""
                        <div class="info-item">
                            <span class="info-label">用户名规范:</span>
                            <span class="info-value" style="color: {color};">
                                {status_icon} {html.escape(user_val.get('message', ''))}
                            </span>
                        </div>
                """

                # 显示具体问题
                issues = user_val.get("issues", [])
                warnings = user_val.get("warnings", [])
                if issues or warnings:
                    problems = issues + warnings
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--info-color); font-size: 0.9em;">
                                问题: {html.escape('; '.join(problems))}
                            </span>
                        </div>
                    """

                # 显示建议
                recommendations = user_val.get("recommendations", [])
                if recommendations:
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--warning-color); font-size: 0.9em;">
                                💡 {html.escape('; '.join(recommendations))}
                            </span>
                        </div>
                    """

                if not user_val.get("valid"):
                    error_items.append(item_html)
                else:
                    warning_items.append(item_html)

            # 显示设置验证（HDR、夜间模式等）
            if "display_settings" in validation:
                display_val = validation["display_settings"]
                if not display_val.get("valid"):
                    status_icon = "❌"
                    color = "var(--error-color)"
                elif display_val.get("warning"):
                    status_icon = "⚠️"
                    color = "var(--warning-color)"
                else:
                    status_icon = "✅"
                    color = "var(--success-color)"

                item_html = f"""
                        <div class="info-item">
                            <span class="info-label">显示设置:</span>
                            <span class="info-value" style="color: {color};">
                                {status_icon} {html.escape(display_val.get('message', ''))}
                            </span>
                        </div>
                """

                # 显示具体问题
                issues = display_val.get("issues", [])
                warnings = display_val.get("warnings", [])
                if issues or warnings:
                    problems = issues + warnings
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--info-color); font-size: 0.9em;">
                                问题: {html.escape('; '.join(problems))}
                            </span>
                        </div>
                    """

                # 显示建议
                recommendations = display_val.get("recommendations", [])
                if recommendations:
                    item_html += f"""
                        <div class="info-item">
                            <span class="info-label"></span>
                            <span class="info-value" style="color: var(--warning-color); font-size: 0.9em;">
                                💡 {html.escape('; '.join(recommendations))}
                            </span>
                        </div>
                    """

                if not display_val.get("valid"):
                    error_items.append(item_html)
                elif display_val.get("warning"):
                    warning_items.append(item_html)
                else:
                    success_items.append(item_html)

            # 生成HTML
            html_content += """
                <div class="info-group">
                    <h3>硬件适配</h3>
                    <div class="info-items">
            """

            # 错误项直接显示
            if error_items:
                html_content += "".join(error_items)

            # 警告项直接显示
            if warning_items:
                html_content += "".join(warning_items)

            # 成功项折叠显示
            if success_items:
                collapse_id = "hardware-success-items"
                html_content += f"""
                    <div style="margin-top: 10px;">
                        <button class="collapse-button" onclick="toggleCollapse('{collapse_id}')">
                            ▶ 显示通过项 ({len(success_items)})
                        </button>
                        <div id="{collapse_id}" style="display: none; margin-top: 5px;">
                """
                html_content += "".join(success_items)
                html_content += """
                        </div>
                    </div>
                """

            html_content += """
                    </div>
                </div>
            """

        html_content += """
                </div>
            </div>
        </div>
        """

        return html_content

    def generate_json(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成系统信息JSON"""
        return {"module": self.name, "title": self.title, "data": system_info}

    def _get_display_name(self, key: str) -> str:
        """获取显示名称"""
        display_names = {
            "os": "操作系统",
            "os_version": "系统版本",
            "os_release": "系统发行版",
            "architecture": "系统架构",
            "machine": "机器类型",
            "processor": "处理器",
            "python_version": "Python版本",
            "python_executable": "Python路径",
            "current_path": "当前路径",
            "user_name": "用户名",
            "computer_name": "计算机名",
            "cpu_model": "CPU型号",
            "cpu_cores_physical": "CPU物理核心",
            "cpu_cores_logical": "CPU逻辑核心",
            "cpu_freq_current": "CPU当前频率",
            "cpu_freq_max": "CPU最大频率",
            "memory_total": "总内存",
            "memory_available": "可用内存",
            "memory_used": "已用内存",
            "memory_percent": "内存使用率",
            "gpu_info": "GPU信息",
            "current_drive": "当前驱动器",
            "disk_type": "磁盘类型",
            "disk_total": "磁盘总容量",
            "disk_used": "已用空间",
            "disk_free": "可用空间",
            "disk_usage_percent": "磁盘使用率",
            # 显示设置
            "hdr_enabled": "HDR",
            "night_light_enabled": "夜间模式/护眼模式",
            "nvidia_filter_enabled": "NVIDIA游戏滤镜",
            "color_filter_enabled": "颜色滤镜",
            "primary_resolution": "主显示器分辨率",
        }
        return display_names.get(key, key)


class SummaryModule(ReportModule):
    """摘要模块"""

    def __init__(self):
        super().__init__("summary", "📊 检测摘要")

    def generate_html(self, summary: Dict[str, Any]) -> str:
        """生成摘要HTML"""
        success_rate = summary.get("success_rate", 0)
        status_class = self._get_status_class(success_rate)

        return f"""
        <div class="section">
            <h2 class="section-title">{self.title}</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-number">{summary.get('total_checks', 0)}</div>
                    <div class="summary-label">总检测项</div>
                </div>
                <div class="summary-item success">
                    <div class="summary-number">{summary.get('completed', 0)}</div>
                    <div class="summary-label">成功项</div>
                </div>
                <div class="summary-item error">
                    <div class="summary-number">{summary.get('failed', 0)}</div>
                    <div class="summary-label">失败项</div>
                </div>
                <div class="summary-item warning">
                    <div class="summary-number">{summary.get('warning_issues', 0)}</div>
                    <div class="summary-label">警告项</div>
                </div>
                <div class="summary-item {status_class}">
                    <div class="summary-number">{success_rate:.1f}%</div>
                    <div class="summary-label">成功率</div>
                </div>
            </div>
        </div>
        """

    def generate_json(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """生成摘要JSON"""
        return {"module": self.name, "title": self.title, "data": summary}

    def _get_status_class(self, success_rate: float) -> str:
        """获取状态样式类"""
        if success_rate >= 90:
            return "success"
        elif success_rate >= 70:
            return "warning"
        else:
            return "error"


class CheckResultsModule(ReportModule):
    """检测结果模块"""

    def __init__(self):
        super().__init__("check_results", "🔍 检测结果")
        # 检测名称中文映射
        self.check_name_map = {
            "system_info": "系统信息",
            "network_connectivity": "网络连通性",
            "environment_dependencies": "环境依赖",
            "path_validation": "路径规范",
            "hardware_compatibility": "硬件适配",
        }

    def generate_html(self, results: List[CheckResult]) -> str:
        """生成检测结果HTML"""
        html_content = f"""
        <div class="section">
            <h2 class="section-title">{self.title}</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                以下是每个检测项的详细信息，包括具体的失败项和警告项。
            </p>
        """

        # 按严重程度排序
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
            # 跳过系统信息检测（已在系统信息模块显示）
            if result.check_name == "system_info":
                continue
            html_content += self._generate_check_item_html(result)

        html_content += """
        </div>
        """

        return html_content

    def generate_json(self, results: List[CheckResult]) -> Dict[str, Any]:
        """生成检测结果JSON"""
        return {
            "module": self.name,
            "title": self.title,
            "data": [
                {
                    "check_name": result.check_name,
                    "status": result.status.value,
                    "severity": result.severity.value,
                    "message": result.message,
                    "details": result.details,
                    "execution_time": result.execution_time,
                    "fix_suggestion": result.fix_suggestion,
                }
                for result in results
            ],
        }

    def _generate_check_item_html(self, result: CheckResult) -> str:
        """生成单个检测项HTML"""
        status_class = f"status-{result.status.value}"
        severity_class = f"check-item {result.severity.value}"

        # 特殊处理不同类型的检测
        if result.check_name == "network_connectivity":
            details_html = self._generate_network_details_html(result)
        elif result.check_name == "hardware_compatibility":
            details_html = self._generate_hardware_compatibility_details_html(result)
        else:
            # 其他检测项的标准处理
            details_html = self._generate_standard_details_html(result)

        fix_suggestion_html = ""
        if result.fix_suggestion:
            fix_suggestion_html = f"""
                <div class="fix-suggestion">
                    <strong>💡 修复建议:</strong> {html.escape(result.fix_suggestion)}
                </div>"""

        # 获取中文名称
        display_name = self.check_name_map.get(result.check_name, result.check_name)

        return f"""
            <div class="{severity_class}">
                <div class="check-header">
                    <div class="check-name">{html.escape(display_name)}</div>
                    <div class="check-status {status_class}">{result.status.value.upper()}</div>
                </div>
                <div class="check-message">{html.escape(result.message)}</div>
                {details_html}
                <div class="check-meta">
                    <small>执行时间: {result.execution_time:.2f}s | 严重程度: {result.severity.value}</small>
                </div>
                {fix_suggestion_html}
            </div>"""

    def _generate_network_details_html(self, result: CheckResult) -> str:
        """生成网络检测的详细信息HTML（按类型分类）"""
        if not result.details:
            return ""

        # 按类型分组
        type_groups = {
            "git_repo": {"name": "Git仓库", "items": []},
            "pypi_source": {"name": "PyPI源", "items": []},
            "mirror_site": {"name": "镜像站点", "items": []},
            "github_proxy": {"name": "GitHub代理", "items": []},
            "project_website": {"name": "项目官网", "items": []},
            "mihoyo_api": {"name": "米哈游API", "items": []},
        }

        # 分类收集
        for url, detail in result.details.items():
            if isinstance(detail, dict):
                item_type = detail.get("type", "unknown")
                item_status = detail.get("status", "unknown")
                response_time = detail.get("response_time_ms", 0)
                error_msg = detail.get("error", "")

                item_info = {
                    "url": url,
                    "status": item_status,
                    "response_time": response_time,
                    "error": error_msg,
                }

                if item_type in type_groups:
                    type_groups[item_type]["items"].append(item_info)

        # 生成HTML
        html_parts = ["<div class='check-details-list'>"]

        for type_key, group_data in type_groups.items():
            items = group_data["items"]
            if not items:
                continue

            type_name = group_data["name"]
            success_items = [item for item in items if item["status"] == "success"]
            failed_items = [
                item
                for item in items
                if item["status"] in ["error", "failure", "timeout"]
            ]

            # 显示分类标题和统计
            html_parts.append(
                f"<div style='margin-top: 15px;'><strong>【{type_name}】</strong> "
            )
            html_parts.append(f"({len(success_items)}/{len(items)} 可用)</div>")

            # 显示成功项
            if success_items:
                html_parts.append(
                    "<div class='success-items' style='margin-left: 20px;'><ul>"
                )
                for item in success_items:
                    url_display = (
                        item["url"].replace("https://", "").replace("http://", "")
                    )
                    if len(url_display) > 60:
                        url_display = url_display[:57] + "..."
                    html_parts.append(
                        f"<li>✅ <strong>{html.escape(url_display)}</strong> "
                        f"<span style='color: #6b7280; font-size: 0.9em;'>({item['response_time']:.0f}ms)</span></li>"
                    )
                html_parts.append("</ul></div>")

            # 失败项折叠显示
            if failed_items:
                collapse_id = f"network-{type_key}-failed-{id(result)}"
                html_parts.append(
                    f"""
                    <div style="margin-left: 20px; margin-top: 5px;">
                        <button class="collapse-button" onclick="toggleCollapse('{collapse_id}')">
                            ▶ 显示不可用源 ({len(failed_items)})
                        </button>
                        <div id="{collapse_id}" style="display: none; margin-top: 5px;">
                            <div class='failed-items'><ul>
                """
                )

                for item in failed_items:
                    url_display = (
                        item["url"].replace("https://", "").replace("http://", "")
                    )
                    if len(url_display) > 60:
                        url_display = url_display[:57] + "..."
                    error_display = (
                        item["error"][:50] + "..."
                        if len(item["error"]) > 50
                        else item["error"]
                    )
                    html_parts.append(
                        f"<li>❌ <strong>{html.escape(url_display)}</strong> "
                        f"<span style='color: #ef4444; font-size: 0.9em;'>({html.escape(error_display)})</span></li>"
                    )

                html_parts.append("</ul></div></div></div>")

        html_parts.append("</div>")
        return "".join(html_parts)

    def _generate_hardware_compatibility_details_html(self, result: CheckResult) -> str:
        """生成硬件适配检测的详细信息HTML"""
        if not result.details:
            return ""

        issues = result.details.get("issues", [])
        warnings = result.details.get("warnings", [])

        if not (issues or warnings):
            return ""

        details_html = "<div class='check-details-list'>"

        # 显示问题
        if issues:
            details_html += "<div class='failed-items'><strong>❌ 失败项:</strong><ul>"
            for issue in issues:
                details_html += f"<li>{html.escape(issue)}</li>"
            details_html += "</ul></div>"

        # 显示警告
        if warnings:
            details_html += "<div class='warning-items'><strong>⚠️ 警告项:</strong><ul>"
            for warning in warnings:
                details_html += f"<li>{html.escape(warning)}</li>"
            details_html += "</ul></div>"

        details_html += "</div>"
        return details_html

    def _generate_standard_details_html(self, result: CheckResult) -> str:
        """生成标准检测项的详细信息HTML（默认隐藏成功项）"""
        if not result.details:
            return ""

        failed_items = []
        warning_items = []
        success_items = []

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

        if not (failed_items or warning_items or success_items):
            return ""

        details_html = "<div class='check-details-list'>"

        # 失败项和警告项直接显示
        if failed_items:
            details_html += "<div class='failed-items'><strong>❌ 失败项:</strong><ul>"
            details_html += "".join(failed_items)
            details_html += "</ul></div>"

        if warning_items:
            details_html += "<div class='warning-items'><strong>⚠️ 警告项:</strong><ul>"
            details_html += "".join(warning_items)
            details_html += "</ul></div>"

        # 成功项默认折叠
        if success_items:
            collapse_id = f"success-items-{id(result)}"
            details_html += f"""
                <div style="margin-top: 10px;">
                    <button class="collapse-button" onclick="toggleCollapse('{collapse_id}')">
                        ▶ 显示通过项 ({len(success_items)})
                    </button>
                    <div id="{collapse_id}" style="display: none; margin-top: 5px;">
                        <div class='success-items'><strong>✅ 通过项:</strong><ul>
            """
            details_html += "".join(success_items)
            details_html += "</ul></div></div></div>"

        details_html += "</div>"
        return details_html


class ReportModuleManager:
    """报告模块管理器"""

    def __init__(self):
        self.modules = {}
        self._register_default_modules()

    def _register_default_modules(self):
        """注册默认模块"""
        self.register_module(SystemInfoModule())
        self.register_module(SummaryModule())
        self.register_module(CheckResultsModule())

    def register_module(self, module: ReportModule):
        """注册模块"""
        self.modules[module.name] = module

    def get_module(self, name: str) -> ReportModule:
        """获取模块"""
        return self.modules.get(name)

    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """生成完整HTML报告"""
        html_parts = []

        # 系统信息
        if "system_info" in data:
            system_module = self.get_module("system_info")
            if system_module:
                html_parts.append(system_module.generate_html(data["system_info"]))

        # 摘要
        if "summary" in data:
            summary_module = self.get_module("summary")
            if summary_module:
                html_parts.append(summary_module.generate_html(data["summary"]))

        # 检测结果
        if "results" in data:
            results_module = self.get_module("check_results")
            if results_module:
                html_parts.append(results_module.generate_html(data["results"]))

        return "\n".join(html_parts)

    def generate_json_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整JSON报告"""
        json_data = {"modules": []}

        # 系统信息
        if "system_info" in data:
            system_module = self.get_module("system_info")
            if system_module:
                json_data["modules"].append(
                    system_module.generate_json(data["system_info"])
                )

        # 摘要
        if "summary" in data:
            summary_module = self.get_module("summary")
            if summary_module:
                json_data["modules"].append(
                    summary_module.generate_json(data["summary"])
                )

        # 检测结果
        if "results" in data:
            results_module = self.get_module("check_results")
            if results_module:
                json_data["modules"].append(
                    results_module.generate_json(data["results"])
                )

        return json_data
