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
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        """加载报告模板"""
        # HTML模板
        self.templates["html"] = {
            "header": self._get_html_header(),
            "footer": self._get_html_footer(),
            "summary": self._get_html_summary_template(),
            "check_item": self._get_html_check_item_template(),
            "critical_issue": self._get_html_critical_issue_template(),
        }

    def generate_report(
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> str:
        """生成报告"""
        if self.config.format == "html":
            return self._generate_html_report(results, project_name, summary)
        elif self.config.format == "json":
            return self._generate_json_report(results, project_name, summary)
        elif self.config.format == "yaml":
            return self._generate_yaml_report(results, project_name, summary)
        elif self.config.format == "markdown":
            return self._generate_markdown_report(results, project_name, summary)
        else:
            logger.warning(f"未知的报告格式: {self.config.format}，使用HTML格式")
            return self._generate_html_report(results, project_name, summary)

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
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> str:
        """生成HTML报告"""
        # 构建报告内容
        content_parts = []

        # 头部
        content_parts.append(self.templates["html"]["header"])

        # 标题和项目信息
        content_parts.append(self._get_html_title_section(project_name))

        # 提取系统信息
        system_info = self._extract_system_info(results)

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
        if critical_results and self.config.include_details:
            content_parts.append(
                self._get_html_critical_issues_section(critical_results)
            )

        # 修复建议汇总
        if self.config.include_fix_suggestions:
            content_parts.append(self._get_html_fix_suggestions_section(results))

        # 底部
        content_parts.append(self.templates["html"]["footer"])

        return "\n".join(content_parts)

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

    def _get_html_header(self) -> str:
        """获取HTML头部模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OOPS 运行预检报告</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --critical-color: #dc2626;
            --info-color: #6b7280;
            --bg-color: #ffffff;
            --text-color: #1f2937;
            --border-color: #e5e7eb;
        }
        
        .dark-mode {
            --bg-color: #1f2937;
            --text-color: #f9fafb;
            --border-color: #374151;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            transition: all 0.3s ease;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .header h1 {
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card.critical { border-left: 4px solid var(--critical-color); }
        .card.error { border-left: 4px solid var(--error-color); }
        .card.warning { border-left: 4px solid var(--warning-color); }
        .card.success { border-left: 4px solid var(--success-color); }
        .card.info { border-left: 4px solid var(--info-color); }
        
        .card-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .critical .card-number { color: var(--critical-color); }
        .error .card-number { color: var(--error-color); }
        .warning .card-number { color: var(--warning-color); }
        .success .card-number { color: var(--success-color); }
        .info .card-number { color: var(--info-color); }
        
        .check-item {
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .check-item.critical { border-left: 4px solid var(--critical-color); }
        .check-item.error { border-left: 4px solid var(--error-color); }
        .check-item.warning { border-left: 4px solid var(--warning-color); }
        .check-item.success { border-left: 4px solid var(--success-color); }
        .check-item.info { border-left: 4px solid var(--info-color); }
        
        .check-details-list {
            margin-top: 10px;
            padding: 10px;
            background: #f9fafb;
            border-radius: 4px;
        }
        
        .check-details-list ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        
        .check-details-list li {
            margin: 5px 0;
            line-height: 1.5;
        }
        
        .failed-items {
            margin-bottom: 10px;
        }
        
        .failed-items strong {
            color: var(--error-color);
        }
        
        .warning-items {
            margin-bottom: 10px;
        }
        
        .warning-items strong {
            color: var(--warning-color);
        }
        
        .success-items {
            margin-bottom: 10px;
        }
        
        .success-items strong {
            color: var(--success-color);
        }
        
        .check-meta {
            margin-top: 10px;
            color: var(--info-color);
        }
        
        .check-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .check-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .check-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .status-success { background: var(--success-color); color: white; }
        .status-warning { background: var(--warning-color); color: white; }
        .status-error { background: var(--error-color); color: white; }
        .status-critical { background: var(--critical-color); color: white; }
        .status-pending { background: var(--info-color); color: white; }
        
        .fix-suggestion {
            background: #fef3c7;
            border-left: 4px solid var(--warning-color);
            padding: 10px 15px;
            margin-top: 10px;
            border-radius: 4px;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: var(--primary-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 5px;
        }
        
        .timestamp {
            color: var(--info-color);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .summary-cards {
                grid-template-columns: 1fr;
            }
            
            .check-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .check-status {
                margin-top: 5px;
            }
        }
        
        /* 系统信息样式 */
        .system-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .info-group {
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            border: 1px solid #e5e7eb;
        }
        
        .info-group h3 {
            margin: 0 0 15px 0;
            color: var(--primary-color);
            font-size: 1.1em;
            font-weight: 600;
        }
        
        .info-items {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .info-item:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: 500;
            color: #374151;
            min-width: 120px;
        }
        
        .info-value {
            color: #6b7280;
            text-align: right;
            font-family: 'Consolas', 'Monaco', monospace;
            word-break: break-all;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .summary-item {
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .summary-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .summary-label {
            color: var(--info-color);
            font-size: 0.9rem;
        }
        
        /* 折叠按钮样式 */
        .collapse-button {
            background: none;
            border: none;
            color: var(--primary-color);
            cursor: pointer;
            font-size: 0.9em;
            padding: 5px 10px;
            margin-left: 10px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .collapse-button:hover {
            background: var(--border-color);
        }
        
        .collapsible-content {
            margin-top: 15px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        /* 统一检测结果样式 */
        .detection-results {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .detection-result {
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .detection-result.warning {
            border-left: 4px solid var(--warning-color);
        }
        
        .detection-result.error {
            border-left: 4px solid var(--error-color);
        }
        
        .detection-result.critical {
            border-left: 4px solid var(--critical-color);
        }
        
        .detection-result.info {
            border-left: 4px solid var(--info-color);
        }
        
        .detection-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .detection-title {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .detection-summary {
            color: var(--info-color);
            font-size: 0.9em;
        }
        
        .detection-message {
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .detection-issues {
            margin-bottom: 15px;
        }
        
        .issue-group {
            margin-bottom: 15px;
        }
        
        .issue-group h4 {
            margin: 0 0 8px 0;
            font-size: 1em;
        }
        
        .issue-group.error h4 {
            color: var(--error-color);
        }
        
        .issue-group.warning h4 {
            color: var(--warning-color);
        }
        
        .issue-group.success h4 {
            color: var(--success-color);
        }
        
        .issue-group ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .issue-group li {
            margin-bottom: 5px;
            line-height: 1.4;
        }
        
        .detection-details {
            background: #f9fafb;
            border-radius: 6px;
            padding: 15px;
            margin-top: 10px;
        }
        
        .fix-suggestion {
            background: #fef3c7;
            border-left: 4px solid var(--warning-color);
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }
        
        .fix-suggestion h4 {
            margin: 0 0 10px 0;
            color: var(--warning-color);
        }
        
        .fix-suggestion p {
            margin: 0;
            line-height: 1.6;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }
        
        .raw-details {
            margin-top: 15px;
        }
        
        .raw-details h4 {
            margin: 0 0 10px 0;
            color: var(--primary-color);
        }
        
        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .detail-group {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px;
        }
        
        .detail-group ul {
            margin: 5px 0;
            padding-left: 20px;
            list-style-type: disc;
            list-style-position: inside;
        }
        
        .detail-group li {
            margin-bottom: 3px;
            line-height: 1.4;
            padding-left: 0;
        }
        
        .detail-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .detail-item:last-child {
            border-bottom: none;
        }
        
        .detail-label {
            font-weight: 500;
            color: #374151;
            min-width: 100px;
            flex-shrink: 0;
        }
        
        .detail-value {
            color: #6b7280;
            text-align: right;
            word-break: break-word;
            margin-left: 10px;
        }
        
        /* 通过项折叠样式 */
        .success-items-section {
            margin: 15px 0;
        }
        
        .success-toggle {
            background: #f0f9ff;
            border: 1px solid var(--success-color);
            color: var(--success-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .success-toggle:hover {
            background: var(--success-color);
            color: white;
        }
        
        /* 详细数据折叠样式 */
        .raw-details-section {
            margin: 15px 0;
        }
        
        .raw-details-toggle {
            background: #fef3c7;
            border: 1px solid var(--warning-color);
            color: var(--warning-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .raw-details-toggle:hover {
            background: var(--warning-color);
            color: white;
        }
        
        .raw-details-section .collapsible-content {
            margin-top: 10px;
            padding: 10px;
            background: #fffbeb;
            border-radius: 6px;
            border: 1px solid #fef3c7;
        }
        
        .raw-details-section .raw-details {
            margin: 0;
        }
        
        .success-items-section .collapsible-content {
            margin-top: 10px;
            padding: 10px;
            background: #f0f9ff;
            border-radius: 6px;
            border: 1px solid #e0f2fe;
        }
        
        .success-items-section .issue-group {
            margin-bottom: 0;
        }
        
        .success-items-section .issue-group ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .success-items-section .issue-group li {
            color: var(--success-color);
            margin-bottom: 4px;
            line-height: 1.4;
        }
        
        /* 优化间距和布局 */
        .detection-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 15px;
            gap: 15px;
        }
        
        .detection-title {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--primary-color);
            flex: 1;
        }
        
        .detection-summary {
            color: var(--info-color);
            font-size: 0.9em;
            flex-shrink: 0;
            text-align: right;
        }
        
        .detection-header .collapse-button {
            margin-left: 0;
            flex-shrink: 0;
        }
        
        /* 修复文字重叠问题 */
        .detection-message {
            margin-bottom: 15px;
            font-weight: 500;
            line-height: 1.5;
            padding: 5px 0;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
        }
        
        .detection-issues {
            margin-bottom: 15px;
            clear: both;
        }
        
        .issue-group {
            margin-bottom: 15px;
            padding: 10px 0;
        }
        
        .issue-group h4 {
            margin: 0 0 10px 0;
            font-size: 1em;
            line-height: 1.3;
        }
        
        .issue-group ul {
            margin: 0;
            padding-left: 25px;
            list-style-type: none;
        }
        
        .issue-group li {
            margin-bottom: 6px;
            line-height: 1.5;
            padding-left: 5px;
            position: relative;
        }
        
        .issue-group.error li::before {
            content: "•";
            color: var(--error-color);
            font-weight: bold;
            position: absolute;
            left: -20px;
        }
        
        .issue-group.warning li::before {
            content: "•";
            color: var(--warning-color);
            font-weight: bold;
            position: absolute;
            left: -20px;
        }
        
        .issue-group.success li::before {
            content: "•";
            color: var(--success-color);
            font-weight: bold;
            position: absolute;
            left: -20px;
        }
        
        /* 缩进项样式（用于网络检测的子项） */
        .issue-group li.indent-item {
            margin-left: 20px;
            font-size: 0.95em;
            color: #6b7280;
        }
        
        .issue-group li.indent-item::before {
            content: "└─";
            left: -25px;
            font-weight: normal;
        }
        
        /* 响应式优化 */
        @media (max-width: 768px) {
            .detection-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .detection-summary {
                text-align: left;
            }
            
            .detection-header .collapse-button {
                align-self: flex-end;
            }
            
            .details-grid {
                grid-template-columns: 1fr;
            }
            
            .system-info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        // 折叠/展开功能
        function toggleCollapse(id) {
            const content = document.getElementById(id);
            const button = event.target;
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                button.textContent = button.textContent.replace('▶', '▼');
            } else {
                content.style.display = 'none';
                button.textContent = button.textContent.replace('▼', '▶');
            }
        }
        
        // 页面加载后默认折叠系统信息
        document.addEventListener('DOMContentLoaded', function() {
            const systemInfoContent = document.getElementById('system-info-content');
            if (systemInfoContent) {
                systemInfoContent.style.display = 'none';
            }
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="report-notice" style="background: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
            <h3 style="margin: 0 0 10px 0; color: #f59e0b;">📋 报告提交说明</h3>
            <p style="margin: 0 0 10px 0;">
                <strong>⚠️ 请勿拍照或截图！</strong>请直接提交 YAML 格式的报告文件。
            </p>
            <p style="margin: 0 0 10px 0;">
                YAML 报告包含完整的检测数据，便于开发者分析问题。
            </p>
            <button onclick="openReportFolder()" style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">
                📁 打开报告文件夹
            </button>
            <span id="yaml-path" style="margin-left: 15px; color: #6b7280; font-size: 14px;"></span>
        </div>
        <script>
            function openReportFolder() {
                // 获取当前 HTML 文件的路径
                const htmlPath = window.location.pathname;
                const reportDir = htmlPath.substring(0, htmlPath.lastIndexOf('/'));
                
                // 尝试打开文件夹（仅在本地文件系统有效）
                if (window.location.protocol === 'file:') {
                    // 显示路径信息
                    const yamlPath = htmlPath.replace('.html', '.yaml');
                    document.getElementById('yaml-path').textContent = 'YAML 报告: ' + yamlPath.split('/').pop();
                    
                    // 提示用户
                    alert('YAML 报告位于同一目录下\\n\\n文件名: ' + yamlPath.split('/').pop() + '\\n\\n请在文件管理器中找到该文件并提交。');
                } else {
                    alert('请在本地打开此报告以访问 YAML 文件。');
                }
            }
        </script>
"""

    def _get_html_footer(self) -> str:
        """获取HTML底部模板"""
        return """
    </div>
</body>
</html>"""

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

    def _get_html_title_section(self, project_name: str) -> str:
        """获取HTML标题部分"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <div class="header">
            <h1>🚀 OOPS 运行预检报告</h1>
            <p style="color: #6b7280; margin: 5px 0;">让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly</p>
            <h2>项目: {html.escape(project_name)}</h2>
            <div class="timestamp">生成时间: {timestamp}</div>
        </div>"""

    def _get_html_summary_section(self, summary: Dict[str, Any]) -> str:
        """获取HTML摘要部分"""
        success_rate = summary.get("success_rate", 0)

        return f"""
        <div class="section">
            <h2 class="section-title">📊 检测摘要</h2>
            <div class="summary-cards">
                <div class="card critical">
                    <div class="card-number">{summary.get('critical_issues', 0)}</div>
                    <div>关键问题</div>
                </div>
                <div class="card error">
                    <div class="card-number">{summary.get('error_issues', 0)}</div>
                    <div>错误问题</div>
                </div>
                <div class="card warning">
                    <div class="card-number">{summary.get('warning_issues', 0)}</div>
                    <div>警告问题</div>
                </div>
                <div class="card success">
                    <div class="card-number">{summary.get('completed', 0)}/{summary.get('total_checks', 0)}</div>
                    <div>完成检测</div>
                </div>
                <div class="card info">
                    <div class="card-number">{success_rate:.1f}%</div>
                    <div>成功率</div>
                </div>
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
        if result.fix_suggestion and self.config.include_fix_suggestions:
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
        self, results: List[CheckResult], project_name: str, summary: Dict[str, Any]
    ) -> Dict[str, str]:
        """生成综合报告（多种格式）"""
        report_paths = {}

        # 生成HTML报告
        html_config = ReportConfig(
            format="html", output_dir=self.output_dir, include_timestamp=True
        )
        html_generator = ReportGenerator(html_config)
        html_report = html_generator.generate_report(results, project_name, summary)
        html_path = html_generator.save_report(html_report, project_name)
        report_paths["html"] = html_path

        # 生成JSON报告
        json_config = ReportConfig(
            format="json", output_dir=self.output_dir, include_timestamp=True
        )
        json_generator = ReportGenerator(json_config)
        json_report = json_generator.generate_report(results, project_name, summary)
        json_path = json_generator.save_report(json_report, project_name)
        report_paths["json"] = json_path

        # 生成Markdown报告
        md_config = ReportConfig(
            format="markdown", output_dir=self.output_dir, include_timestamp=True
        )
        md_generator = ReportGenerator(md_config)
        md_report = md_generator.generate_report(results, project_name, summary)
        md_path = md_generator.save_report(md_report, project_name)
        report_paths["markdown"] = md_path

        return report_paths
