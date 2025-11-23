"""
HTML 渲染器模块
从数据模型生成 HTML 报告，实现数据和渲染的完全分离
"""

from typing import Dict, Any
from oops.core.data_models import DiagnosticReport, SystemInfoData
import html


class HTMLRenderer:
    """HTML 渲染器 - 从数据模型生成 HTML"""
    
    def __init__(self):
        self.styles = self._get_styles()
        self.scripts = self._get_scripts()
    
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
        return f"""
        <div class="header">
            <h1>🔍 OOPS 诊断报告</h1>
            <div class="project-info">
                <p><strong>项目:</strong> {html.escape(report.project_name)}</p>
                <p><strong>项目路径:</strong> {html.escape(report.project_path)}</p>
                <p><strong>运行路径:</strong> {html.escape(report.current_path)}</p>
                <p><strong>生成时间:</strong> {html.escape(report.timestamp)}</p>
            </div>
        </div>
        """
    
    def _render_summary(self, summary: Dict[str, Any]) -> str:
        """渲染摘要卡片"""
        return f"""
        <div class="section">
            <h2 class="section-title">📊 检测摘要</h2>
            <div class="summary-cards">
                <div class="card success">
                    <div class="card-number">{summary.get('completed', 0)}</div>
                    <div class="card-label">成功完成</div>
                </div>
                <div class="card error">
                    <div class="card-number">{summary.get('failed', 0)}</div>
                    <div class="card-label">执行失败</div>
                </div>
                <div class="card critical">
                    <div class="card-number">{summary.get('critical_issues', 0)}</div>
                    <div class="card-label">关键问题</div>
                </div>
                <div class="card warning">
                    <div class="card-number">{summary.get('warning_issues', 0)}</div>
                    <div class="card-label">警告</div>
                </div>
                <div class="card info">
                    <div class="card-number">{summary.get('success_rate', 0):.1f}%</div>
                    <div class="card-label">成功率</div>
                </div>
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
            html_parts.append('<div class="info-group"><h3>基本信息</h3><div class="info-items">')
            for key, value in system_data.basic.items():
                display_name = self._get_display_name(key)
                html_parts.append(f'''
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                ''')
            html_parts.append('</div></div>')
        
        # 硬件信息
        if system_data.hardware:
            html_parts.append('<div class="info-group"><h3>硬件信息</h3><div class="info-items">')
            for key, value in system_data.hardware.items():
                display_name = self._get_display_name(key)
                html_parts.append(f'''
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                ''')
            html_parts.append('</div></div>')
        
        # 存储信息
        if system_data.storage:
            html_parts.append('<div class="info-group"><h3>存储信息</h3><div class="info-items">')
            for key, value in system_data.storage.items():
                display_name = self._get_display_name(key)
                html_parts.append(f'''
                <div class="info-item">
                    <span class="info-label">{display_name}:</span>
                    <span class="info-value">{html.escape(str(value))}</span>
                </div>
                ''')
            html_parts.append('</div></div>')
        
        html_parts.append('</div>')
        return ''.join(html_parts)
    
    def _render_check_results(self, check_results: Dict[str, Any]) -> str:
        """渲染检测结果"""
        if not check_results:
            return ""
        
        html_parts = ['<div class="section"><h2 class="section-title">🔍 检测结果</h2>']
        
        for check_name, result in check_results.items():
            severity = result.get('severity', 'info')
            status = result.get('status', 'unknown')
            message = result.get('message', '')
            
            html_parts.append(f'''
            <div class="check-item {severity}">
                <div class="check-header">
                    <div class="check-name">{html.escape(check_name)}</div>
                    <span class="check-status status-{status}">{status}</span>
                </div>
                <div class="check-message">{html.escape(message)}</div>
            </div>
            ''')
        
        html_parts.append('</div>')
        return ''.join(html_parts)
    
    def _render_issues(self, issues: Dict[str, Any]) -> str:
        """渲染问题列表"""
        total_issues = len(issues.get('critical', [])) + len(issues.get('errors', [])) + len(issues.get('warnings', []))
        
        if total_issues == 0:
            return ""
        
        html_parts = [f'<div class="section"><h2 class="section-title">⚠️ 发现的问题 ({total_issues})</h2>']
        
        # 关键问题
        if issues.get('critical'):
            html_parts.append('<h3 style="color: var(--critical-color);">🔴 关键问题</h3>')
            for issue in issues['critical']:
                html_parts.append(f'''
                <div class="issue-item critical">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                ''')
        
        # 错误
        if issues.get('errors'):
            html_parts.append('<h3 style="color: var(--error-color);">❌ 错误</h3>')
            for issue in issues['errors']:
                html_parts.append(f'''
                <div class="issue-item error">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                ''')
        
        # 警告
        if issues.get('warnings'):
            html_parts.append('<h3 style="color: var(--warning-color);">⚠️ 警告</h3>')
            for issue in issues['warnings']:
                html_parts.append(f'''
                <div class="issue-item warning">
                    <strong>{html.escape(issue['check'])}</strong>: {html.escape(issue['message'])}
                    {f'<div class="fix-suggestion">💡 {html.escape(issue["suggestion"])}</div>' if issue.get('suggestion') else ''}
                </div>
                ''')
        
        html_parts.append('</div>')
        return ''.join(html_parts)
    
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
    
    def _get_styles(self) -> str:
        """获取 CSS 样式"""
        return """
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
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: #f9fafb;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: var(--primary-color);
            margin-bottom: 15px;
        }
        
        .project-info p {
            margin: 5px 0;
            color: var(--info-color);
        }
        
        .section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: var(--primary-color);
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }
        
        .card.success { border-color: var(--success-color); background: #f0fdf4; }
        .card.error { border-color: var(--error-color); background: #fef2f2; }
        .card.critical { border-color: var(--critical-color); background: #fef2f2; }
        .card.warning { border-color: var(--warning-color); background: #fffbeb; }
        .card.info { border-color: var(--info-color); background: #f9fafb; }
        
        .card-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .card.success .card-number { color: var(--success-color); }
        .card.error .card-number { color: var(--error-color); }
        .card.critical .card-number { color: var(--critical-color); }
        .card.warning .card-number { color: var(--warning-color); }
        .card.info .card-number { color: var(--info-color); }
        
        .check-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .check-item.critical { border-color: var(--critical-color); background: #fef2f2; }
        .check-item.error { border-color: var(--error-color); background: #fef2f2; }
        .check-item.warning { border-color: var(--warning-color); background: #fffbeb; }
        .check-item.info { border-color: var(--info-color); background: #f9fafb; }
        
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
            background: var(--info-color);
            color: white;
        }
        
        .system-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .info-group h3 {
            margin-bottom: 10px;
            color: var(--primary-color);
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .info-label {
            font-weight: 500;
            color: var(--info-color);
        }
        
        .info-value {
            font-weight: 600;
        }
        
        .collapse-button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .collapsible-content {
            display: none;
            margin-top: 15px;
        }
        
        .issue-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .issue-item.critical { border-color: var(--critical-color); background: #fef2f2; }
        .issue-item.error { border-color: var(--error-color); background: #fef2f2; }
        .issue-item.warning { border-color: var(--warning-color); background: #fffbeb; }
        
        .fix-suggestion {
            margin-top: 10px;
            padding: 10px;
            background: #fef3c7;
            border-radius: 4px;
        }
        """
    
    def _get_scripts(self) -> str:
        """获取 JavaScript 脚本"""
        return """
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
        """
