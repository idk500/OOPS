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
            SeverityLevel.CRITICAL: "🔴"
        }
        
        self.severity_colors = {
            SeverityLevel.INFO: "var(--info-color)",
            SeverityLevel.WARNING: "var(--warning-color)",
            SeverityLevel.ERROR: "var(--error-color)", 
            SeverityLevel.CRITICAL: "var(--critical-color)"
        }

    def render_detection_result(self, result: CheckResult) -> str:
        """
        渲染单个检测结果
        
        格式要求：
        - 折叠显示，但显示所有通过项
        - 默认显示所有警告/错误项
        """
        # 跳过系统信息检测器（已在系统信息模块显示）
        if result.check_name in ["system_info", "hardware_info", "system_info_new"]:
            return ""
        
        # 提取检测项详情
        success_items, warning_items, error_items = self._extract_detection_items(result)
        
        # 生成摘要信息
        summary = self._generate_summary(result, success_items, warning_items, error_items)
        
        # 生成HTML
        html_content = f"""
        <div class="detection-result {result.severity.value}">
            <div class="detection-header">
                <div class="detection-title">
                    {self.severity_icons[result.severity]} {self._get_display_name(result.check_name)}
                </div>
                <div class="detection-summary">{summary}</div>
                <button class="collapse-button" onclick="toggleCollapse('{result.check_name}-details')">
                    ▶ 详细信息
                </button>
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
                    html_content += f"<li>{html.escape(item)}</li>"
                html_content += "</ul></div>"
                
            html_content += '</div>'
        
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

    def _extract_detection_items(self, result: CheckResult) -> tuple[List[str], List[str], List[str]]:
        """从检测结果中提取成功、警告、错误项"""
        success_items = []
        warning_items = []
        error_items = []
        
        if not result.details:
            return success_items, warning_items, error_items
        
        # 处理不同检测器的数据结构
        if result.check_name == "system_settings":
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
                            type_groups[item_type]["success"].append(f"{url_display} ({response_time:.0f}ms)")
                        elif item_status in ["error", "timeout", "failure"]:
                            error_display = error_msg[:30] + "..." if len(error_msg) > 30 else error_msg
                            type_groups[item_type]["failed"].append(f"{url_display}: {error_display}")
            
            # 生成分类摘要
            for type_key, group_data in type_groups.items():
                success_count = len(group_data["success"])
                failed_count = len(group_data["failed"])
                total_count = success_count + failed_count
                
                if total_count > 0:
                    type_name = group_data["name"]
                    if success_count > 0:
                        success_items.append(f"{type_name}: {success_count}/{total_count} 可用")
                        # 添加具体的成功项到详细列表
                        for item in group_data["success"]:
                            success_items.append(f"  └─ {item}")
                    
                    if failed_count > 0:
                        error_items.append(f"{type_name}: {failed_count} 项不可用")
                        # 只添加前3个失败项到错误列表，避免过长
                        for item in group_data["failed"][:3]:
                            error_items.append(f"  └─ {item}")
                        if failed_count > 3:
                            error_items.append(f"  └─ ... 还有 {failed_count - 3} 项")
                        
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

    def _generate_summary(self, result: CheckResult, success_items: List[str], 
                         warning_items: List[str], error_items: List[str]) -> str:
        """生成检测结果摘要"""
        total_items = len(success_items) + len(warning_items) + len(error_items)
        
        if total_items == 0:
            return "无详细项目"
        
        summary_parts = []
        if success_items:
            summary_parts.append(f"✅ {len(success_items)}项通过")
        if warning_items:
            summary_parts.append(f"⚠️ {len(warning_items)}项警告")
        if error_items:
            summary_parts.append(f"❌ {len(error_items)}项错误")
            
        return " | ".join(summary_parts)

    def _render_raw_details(self, details: Dict[str, Any], check_name: str = "") -> str:
        """渲染原始详细信息 - 直接显示在详细信息区域"""
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
                    html_content += f"<li>{self._get_display_name(sub_key)}: {html.escape(str(sub_value))}</li>"
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