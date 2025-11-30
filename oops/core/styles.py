"""
集中管理的 CSS 样式模块
所有 HTML 报告的样式在此统一定义
"""


class ReportStyles:
    """报告样式管理器"""

    @staticmethod
    def get_css_variables() -> str:
        """CSS 变量定义"""
        return """
        :root {
            --primary-color: #2563eb;
            --secondary-color: #6b7280;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --critical-color: #dc2626;
            --info-color: #3b82f6;
            --bg-color: #f9fafb;
            --card-bg: #ffffff;
            --border-color: #e5e7eb;
            --text-color: #111827;
            --text-secondary: #6b7280;
        }
        """

    @staticmethod
    def get_base_styles() -> str:
        """基础样式"""
        return """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        h1 {
            color: var(--primary-color);
            margin-bottom: 10px;
            font-size: 28px;
        }

        h2 {
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 24px;
        }

        h3 {
            color: var(--text-color);
            margin-bottom: 10px;
            font-size: 18px;
        }

        .section {
            background-color: var(--card-bg);
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 15px;
        }

        .section-title {
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 8px;
            margin-bottom: 15px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        .section-header .section-title {
            border-bottom: none;
            padding-bottom: 0;
            margin-bottom: 0;
        }

        .system-summary-row {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            flex-wrap: wrap;
            gap: 15px;
            margin: 8px 0;
        }

        .system-summary-text {
            color: #6b7280;
            flex: 1;
            min-width: 0;
            max-width: calc(100% - 140px); /* 留出按钮和间距空间 */
            word-wrap: break-word;
        }

        .footer {
            text-align: center;
            color: var(--text-secondary);
            font-size: 14px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }
        """

    @staticmethod
    def get_component_styles() -> str:
        """组件样式（卡片、按钮、表格等）"""
        return """
        /* 操作按钮样式 */
        .action-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }

        .action-button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.2s;
        }

        .action-button:hover {
            background: #1d4ed8;
        }

        .action-button:active {
            background: #1e40af;
        }

        .collapse-button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .collapse-button:hover {
            background: #1d4ed8;
        }

        .collapsible-content {
            display: none;
            margin-top: 15px;
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

        .info-items {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }

        .info-label {
            font-weight: 500;
            color: var(--text-secondary);
        }

        .info-value {
            font-weight: 600;
        }

        .summary-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
            padding: 10px;
            background: #f9fafb;
            border-radius: 8px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            padding: 6px 12px;
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            white-space: nowrap;
        }

        .stat-label {
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 13px;
        }

        .stat-value {
            font-weight: 700;
            font-size: 14px;
            color: var(--primary-color);
        }

        .check-item {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            background-color: var(--bg-color);
        }

        .check-item.critical {
            border-left-color: var(--critical-color);
        }

        .check-item.error {
            border-left-color: var(--error-color);
        }

        .check-item.warning {
            border-left-color: var(--warning-color);
        }

        .check-item.info {
            border-left-color: var(--info-color);
        }

        .check-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .check-name {
            font-weight: 600;
            font-size: 16px;
        }

        .check-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-completed {
            background-color: var(--success-color);
            color: white;
        }

        .status-failed {
            background-color: var(--error-color);
            color: white;
        }

        .status-skipped {
            background-color: var(--secondary-color);
            color: white;
        }

        .status-pending {
            background-color: var(--warning-color);
            color: white;
        }

        .check-message {
            margin-bottom: 10px;
            color: var(--text-color);
        }

        .check-details-list {
            margin-left: 20px;
            margin-bottom: 10px;
        }

        .check-details-list ul {
            margin-left: 20px;
        }

        .check-meta {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 10px;
        }

        .fix-suggestion {
            margin-top: 10px;
            padding: 10px;
            background-color: #f3f4f6;
            border-radius: 4px;
            border-left: 3px solid var(--warning-color);
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
        """

    @staticmethod
    def get_detection_styles() -> str:
        """检测结果相关样式"""
        return """
        .detection-results {
            margin-top: 20px;
        }

        .detection-result {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
            background-color: var(--bg-color);
        }

        .detection-result.critical {
            border-left-color: var(--critical-color);
        }

        .detection-result.error {
            border-left-color: var(--error-color);
        }

        .detection-result.warning {
            border-left-color: var(--warning-color);
        }

        .detection-result.info {
            border-left-color: var(--info-color);
        }

        .detection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .detection-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .detection-title {
            font-weight: 600;
            font-size: 16px;
        }

        .detection-summary {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .detection-message {
            margin-bottom: 10px;
            color: var(--text-color);
        }

        .detection-issues {
            margin-top: 15px;
        }

        .issue-group {
            margin-bottom: 15px;
        }

        .issue-group h4 {
            margin-bottom: 8px;
            font-size: 14px;
            font-weight: 600;
        }

        .issue-group ul {
            margin-left: 20px;
        }

        .issue-group li {
            margin-bottom: 4px;
            line-height: 1.4;
        }

        .indent-item {
            margin-left: 20px !important;
        }

        .detection-details {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }

        .raw-details {
            margin-top: 15px;
        }

        .raw-details h4 {
            margin-bottom: 10px;
            font-size: 16px;
            font-weight: 600;
            color: var(--primary-color);
        }

        .details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .detail-group {
            margin-bottom: 15px;
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }

        .detail-group strong {
            display: block;
            margin-bottom: 8px;
            color: var(--primary-color);
            font-size: 14px;
        }

        /* YAML 路径显示 */
        .yaml-path-display {
            display: none;
            margin-top: 10px;
            padding: 10px 15px;
            background: #f3f4f6;
            border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            word-break: break-all;
        }

        .yaml-path-display.show {
            display: block;
        }

        .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }

        .detail-label {
            font-weight: 500;
            color: var(--text-secondary);
        }

        .detail-value {
            font-weight: 600;
        }
        """

    @staticmethod
    def get_responsive_styles() -> str:
        """响应式设计样式"""
        return """
        /* 响应式设计 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }

            h1 {
                font-size: 24px;
            }

            h2 {
                font-size: 20px;
            }

            .check-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }

            .detection-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }

            .summary-stats-grid {
                flex-direction: column;
                gap: 6px;
            }

            .stat-item {
                padding: 6px 10px;
                width: 100%;
            }

            .system-info-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }

            .details-grid {
                grid-template-columns: 1fr;
                gap: 10px;
            }
        }
        """

    @staticmethod
    def get_full_stylesheet() -> str:
        """获取完整样式表"""
        return f"""
        {ReportStyles.get_css_variables()}
        {ReportStyles.get_base_styles()}
        {ReportStyles.get_component_styles()}
        {ReportStyles.get_detection_styles()}
        {ReportStyles.get_responsive_styles()}
        """
