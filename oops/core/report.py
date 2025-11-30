"""
报告生成模块
负责生成HTML、JSON等格式的诊断报告
"""

import html
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from oops.core.diagnostics import CheckResult, SeverityLevel
from oops.core.html_renderer import HTMLRenderer
from oops.core.report_modules import ReportModuleManager

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """报告配置"""

    format: str = "html"  # html, json, markdown
    output_dir: str = "reports"
    include_timestamp: bool = True
    include_summary: bool = True
    include_details: bool = True
    include_fix_suggestions: bool = True
    theme: str = "light"  # light, dark


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()

    def generate_report(
        self,
        results: List[CheckResult],
        project_name: str,
        summary: Dict[str, Any],
        yaml_path: str = "",
        project_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """生成报告

        Args:
            results: 检测结果列表
            project_name: 项目名称
            summary: 摘要信息
            yaml_path: YAML报告路径（用于HTML报告显示）
        """
        if self.config.format == "html":
            return self._generate_html_report(
                results, project_name, summary, yaml_path, project_config
            )
        elif self.config.format == "json":
            return self._generate_json_report(results, project_name, summary)
        elif self.config.format == "yaml":
            return self._generate_yaml_report(results, project_name, summary)
        elif self.config.format == "markdown":
            return self._generate_markdown_report(results, project_name, summary)
        else:
            logger.warning(f"未知的报告格式: {self.config.format}，使用HTML格式")
            return self._generate_html_report(
                results, project_name, summary, yaml_path, project_config
            )

    def save_report(self, report_content: str, project_name: str) -> str:
        """保存报告到文件"""
        # 创建输出目录
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.config.include_timestamp:
            filename = f"oops_report_{project_name}_{timestamp}.{self.config.format}"
        else:
            filename = f"oops_report_{project_name}.{self.config.format}"

        file_path = output_dir / filename

        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"报告已保存: {file_path}")
        return str(file_path)

    def _generate_html_report(
        self,
        results: List[CheckResult],
        project_name: str,
        summary: Dict[str, Any],
        yaml_path: str = "",
        project_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """生成HTML报告

        Args:
            results: 检测结果列表
            project_name: 项目名称
            summary: 摘要信息
            yaml_path: YAML报告路径（可选，用于在HTML中显示）
        """
        # 提取系统信息
        system_info = self._extract_system_info(results)

        # 获取 OOPS 版本号
        from oops import __version__ as oops_version

        # 生成简报（用于复制按钮）
        from oops.core.brief_report import BriefReportGenerator

        brief_texts = BriefReportGenerator.generate_text_brief(
            project_name,
            summary,
            results,
            system_info,
            oops_version=oops_version,
            project_config=project_config,
        )

        # 使用HTMLRenderer类生成完整报告
        renderer = HTMLRenderer(
            include_details=self.config.include_details,
            include_fix_suggestions=self.config.include_fix_suggestions,
        )
        return renderer.render_full_report(
            results,
            project_name,
            summary,
            system_info,
            oops_version,
            brief_texts,
            yaml_path,
            project_config,
        )

    def _generate_json_report(
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> str:
        """生成JSON报告"""
        report_data = {
            "project": project_name,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": [asdict(result) for result in results],
            "fix_suggestions": self._extract_fix_suggestions(results),
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def _generate_yaml_report(
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> str:
        """生成YAML报告 - 用于用户提交给项目开发者"""
        from oops.core.data_models import create_diagnostic_report_from_results

        # 使用数据模型创建报告
        report = create_diagnostic_report_from_results(
            results=results,
            project_name=project_name,
            project_path="",  # 将在后续从配置中获取
            summary=summary,
        )

        # 转换为 YAML
        return report.to_yaml()

    def _generate_markdown_report(
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> str:
        """生成Markdown报告"""
        content_parts = []

        # 标题
        content_parts.append(f"# OOPS 诊断报告 - {project_name}")
        content_parts.append(
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        content_parts.append("")

        # 摘要
        if self.config.include_summary:
            content_parts.append("## 📊 检测摘要")
            content_parts.append(f"- **总检测项**: {summary.get('total_checks', 0)}")
            content_parts.append(f"- **成功完成**: {summary.get('completed', 0)}")
            content_parts.append(f"- **执行失败**: {summary.get('failed', 0)}")
            content_parts.append(f"- **关键问题**: {summary.get('critical_issues', 0)}")
            content_parts.append(f"- **错误问题**: {summary.get('error_issues', 0)}")
            content_parts.append(f"- **警告问题**: {summary.get('warning_issues', 0)}")
            content_parts.append(f"- **成功率**: {summary.get('success_rate', 0):.1f}%")
            content_parts.append("")

        # 关键问题
        critical_results = [r for r in results if r.severity == SeverityLevel.CRITICAL]
        if critical_results and self.config.include_details:
            content_parts.append("## 🚨 关键问题")
            for result in critical_results:
                content_parts.append(f"### ❌ {result.check_name}")
                content_parts.append(f"- **状态**: {result.status.value}")
                content_parts.append(f"- **消息**: {result.message}")
                if result.fix_suggestion:
                    content_parts.append(f"- **修复建议**: {result.fix_suggestion}")
                content_parts.append("")

        # 详细结果
        if self.config.include_details:
            content_parts.append("## 🔍 详细检测结果")
            for result in results:
                status_emoji = self._get_status_emoji(result.status.value)
                severity_emoji = self._get_severity_emoji(result.severity)

                content_parts.append(
                    f"### {severity_emoji} {result.check_name} {status_emoji}"
                )
                content_parts.append(f"- **状态**: {result.status.value}")
                content_parts.append(f"- **严重程度**: {result.severity.value}")
                content_parts.append(f"- **消息**: {result.message}")
                content_parts.append(f"- **执行时间**: {result.execution_time:.2f}秒")
                if result.fix_suggestion:
                    content_parts.append(f"- **修复建议**: {result.fix_suggestion}")
                content_parts.append("")

        # 修复建议
        if self.config.include_fix_suggestions:
            content_parts.append("## 🛠️ 修复建议汇总")
            fix_suggestions = self._extract_fix_suggestions(results)
            for category, suggestions in fix_suggestions.items():
                if suggestions:
                    content_parts.append(f"### {category}")
                    for suggestion in suggestions:
                        content_parts.append(f"- {suggestion}")
                    content_parts.append("")

        return "\n".join(content_parts)

    def _extract_system_info(self, results: List[CheckResult]) -> Dict[str, Any]:
        """从检测结果中提取系统信息 - 支持新旧检测器"""
        system_info = {}

        # 尝试从新检测器获取数据
        for result in results:
            if result.check_name == "hardware_info":
                # 新的硬件检测器
                hardware_data = result.details
                system_info["hardware"] = {
                    "cpu_model": hardware_data.get("cpu", {}).get("model"),
                    "cpu_cores_physical": hardware_data.get("cpu", {}).get(
                        "cores_physical"
                    ),
                    "cpu_cores_logical": hardware_data.get("cpu", {}).get(
                        "cores_logical"
                    ),
                    "cpu_freq_current": hardware_data.get("cpu", {}).get(
                        "freq_current"
                    ),
                    "cpu_freq_max": hardware_data.get("cpu", {}).get("freq_max"),
                    "memory_total": hardware_data.get("memory", {}).get("total"),
                    "memory_available": hardware_data.get("memory", {}).get(
                        "available"
                    ),
                    "memory_used": hardware_data.get("memory", {}).get("used"),
                    "memory_percent": hardware_data.get("memory", {}).get("percent"),
                    "gpu_info": hardware_data.get("gpu"),
                }
                system_info["storage"] = {
                    "current_drive": hardware_data.get("storage", {}).get(
                        "current_drive"
                    ),
                    "disk_total": hardware_data.get("storage", {}).get("total"),
                    "disk_used": hardware_data.get("storage", {}).get("used"),
                    "disk_free": hardware_data.get("storage", {}).get("free"),
                    "disk_usage_percent": hardware_data.get("storage", {}).get(
                        "percent"
                    ),
                    "disk_type": hardware_data.get("storage", {}).get("type"),
                }
            elif result.check_name == "system_info_new":
                # 新的系统检测器
                sys_data = result.details
                system_info["basic"] = {
                    "os": sys_data.get("os", {}).get("name"),
                    "os_version": sys_data.get("os", {}).get("version"),
                    "os_release": sys_data.get("os", {}).get("release"),
                    "architecture": sys_data.get("os", {}).get("architecture"),
                    "machine": sys_data.get("os", {}).get("machine"),
                    "processor": sys_data.get("os", {}).get("processor"),
                    "python_version": sys_data.get("python", {}).get("version"),
                    "python_executable": sys_data.get("python", {}).get("executable"),
                    "current_path": sys_data.get("paths", {}).get("current"),
                }
            elif result.check_name == "system_settings":
                # 新的系统设置检测器
                settings_data = result.details.get("settings", {})
                if not system_info.get("basic"):
                    system_info["basic"] = {}
                # 将系统设置添加到 basic 中
                system_info["basic"].update(
                    {
                        "hdr_enabled": settings_data.get("hdr_enabled", False),
                        "night_light_enabled": settings_data.get(
                            "night_light_enabled", False
                        ),
                        "color_filter_enabled": settings_data.get(
                            "color_filter_enabled", False
                        ),
                        "primary_resolution": settings_data.get("primary_resolution"),
                    }
                )

        # 如果新检测器没有数据，尝试从旧检测器获取
        if not system_info:
            for result in results:
                if result.check_name == "system_info":
                    system_info = result.details.copy()
                    if hasattr(result, "details") and "validation" in result.details:
                        system_info["validation"] = result.details["validation"]
                    return system_info

        return system_info



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

    def _get_status_emoji(self, status: str) -> str:
        """获取状态表情符号"""
        emoji_map = {
            "completed": "✅",
            "running": "🔄",
            "failed": "❌",
            "skipped": "⏭️",
            "pending": "⏳",
        }
        return emoji_map.get(status, "❓")

    def _get_severity_emoji(self, severity: SeverityLevel) -> str:
        """获取严重程度表情符号"""
        emoji_map = {
            SeverityLevel.CRITICAL: "💥",
            SeverityLevel.ERROR: "❌",
            SeverityLevel.WARNING: "⚠️",
            SeverityLevel.INFO: "ℹ️",
        }
        return emoji_map.get(severity, "❓")

    def _get_html_summary_template(self) -> str:
        """获取HTML摘要模板（占位符）"""
        return ""

    def _get_html_check_item_template(self) -> str:
        """获取HTML检测项模板（占位符）"""
        return ""

    def _get_html_critical_issue_template(self) -> str:
        """获取HTML关键问题模板（占位符）"""
        return ""


class ReportManager:
    """报告管理器 - 简化报告生成流程"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir

    def generate_comprehensive_report(
        self,
        results: List[CheckResult],
        project_name: str,
        summary: Dict[str, Any],
        project_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """生成综合报告（多种格式）"""
        report_paths = {}

        # 生成HTML报告
        html_config = ReportConfig(
            format="html", output_dir=self.output_dir, include_timestamp=True
        )
        html_generator = ReportGenerator(html_config)
        html_report = html_generator.generate_report(
            results, project_name, summary, project_config=project_config
        )
        html_path = html_generator.save_report(html_report, project_name)
        report_paths["html"] = html_path

        # 生成JSON报告
        json_config = ReportConfig(
            format="json", output_dir=self.output_dir, include_timestamp=True
        )
        json_generator = ReportGenerator(json_config)
        json_report = json_generator.generate_report(
            results, project_name, summary, project_config=project_config
        )
        json_path = json_generator.save_report(json_report, project_name)
        report_paths["json"] = json_path

        # 生成Markdown报告
        md_config = ReportConfig(
            format="markdown", output_dir=self.output_dir, include_timestamp=True
        )
        md_generator = ReportGenerator(md_config)
        md_report = md_generator.generate_report(
            results, project_name, summary, project_config=project_config
        )
        md_path = md_generator.save_report(md_report, project_name)
        report_paths["markdown"] = md_path

        return report_paths
