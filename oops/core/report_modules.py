"""
报告模块化组件
将报告生成拆分为独立的模块
"""

import html
from typing import Any, Dict, List

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
            system_info.get("basic")
            or system_info.get("hardware")
            or system_info.get("storage")
            or system_info.get("validation")
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
            summary_parts.append(f"磁盘: {storage['disk_type']}")
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
                        # 其他显示设置只显示状态，不显示判断性图标
                        status_text = (
                            "启用"
                            if value is True
                            else "禁用" if value is False else str(value)
                        )
                        html_content += f"""
                            <div class="info-item">
                                <span class="info-label">{display_name}:</span>
                                <span class="info-value">{html.escape(status_text)}</span>
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
                # 所有存储信息统一处理，不显示警告
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

        # 移除所有硬件适配验证逻辑 - 这些应该在独立的检测器中处理
        # 系统信息模块只负责展示纯数据，不做任何验证或判断

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
    """检测结果模块 - 使用统一渲染器"""

    def __init__(self):
        super().__init__("check_results", "🔍 检测结果")
        # 导入统一渲染器
        from oops.core.unified_renderer import UnifiedDetectionRenderer

        self.unified_renderer = UnifiedDetectionRenderer()

    def generate_html(self, results: List[CheckResult]) -> str:
        """生成检测结果HTML - 使用统一格式"""
        html_content = f"""
        <div class="section">
            <h2 class="section-title">{self.title}</h2>
            <p style="color: #6b7280; margin-bottom: 20px;">
                以下是每个检测项的详细信息，按照统一格式显示。错误和警告项默认展开，通过项可展开查看。
            </p>
            <div class="detection-results">
        """

        # 按指定顺序排序检测结果
        check_order = {
            "hardware_info": 1,
            "system_info_new": 2,
            "system_settings": 3,
            "network_connectivity": 4,
            "python_environment": 5,
            "environment_dependencies": 6,
            "path_validation": 7,
            "game_settings": 8,  # 游戏内设置（待开发）
        }

        # 按照指定顺序排序，未指定的放在最后
        sorted_results = sorted(
            results, key=lambda r: check_order.get(r.check_name, 999)
        )

        # 使用统一渲染器渲染每个检测结果
        for result in sorted_results:
            rendered_result = self.unified_renderer.render_detection_result(result)
            if rendered_result:  # 统一渲染器会跳过系统信息等
                html_content += rendered_result

        # 添加游戏内设置占位项
        html_content += """
        <div class="detection-result info">
            <div class="detection-header">
                <div class="detection-title">
                    🎮 游戏内设置
                </div>
                <div class="detection-summary">功能开发中</div>
            </div>
            
            <div class="detection-message" style="color: var(--info-color);">
                此功能正在开发中，敬请期待
            </div>
        </div>
        """

        html_content += """
            </div>
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
                if result.check_name
                not in ["system_info", "hardware_info", "system_info_new"]
            ],
        }


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
