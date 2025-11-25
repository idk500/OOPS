"""
简报生成器
生成适合快速分享的简短报告（500字符以内）
"""

from typing import Any, Dict, List


class BriefReportGenerator:
    """简报生成器 - 生成简短的检测报告"""

    @staticmethod
    def generate_text_brief(
        project_name: str,
        summary: Dict[str, Any],
        results: List[Any],
        system_info: Dict[str, Any],
        report_path: str = "",
        oops_version: str = "",
    ) -> List[str]:
        """
        生成文本格式简报（适合QQ/微信/论坛）

        新格式：
        OOPS_v0.2.1, Zenless_OD, 通过项(8/9)
        - 硬件信息(5/1/0): 非SSD
        - 系统设置(4/0/1): 未以管理员权限运行

        Args:
            project_name: 项目名称
            summary: 检测摘要
            results: 检测结果列表
            system_info: 系统信息
            report_path: 完整报告路径
            oops_version: OOPS 版本号

        Returns:
            简报列表（每个元素不超过2000字符）
        """
        # 第一行：版本和通过率
        total = summary.get("total_checks", 0)
        completed = summary.get("completed", 0)

        # 简化项目名称
        project_short = BriefReportGenerator._shorten_project_name(project_name)

        header = f"OOPS_v{oops_version}, {project_short}, 通过项({completed}/{total})"

        # 收集所有检测项的详细信息
        detail_lines = []

        for result in results:
            # 跳过成功且无警告的项
            if result.severity.value == "info" and not result.details.get("warnings"):
                continue

            # 统计该检测项的状态
            stats = BriefReportGenerator._get_check_stats(result)
            success_count = stats["success"]
            warning_count = stats["warning"]
            error_count = stats["error"]

            # 获取简短的问题描述
            issue_desc = BriefReportGenerator._get_issue_description(result)

            # 检测器名称
            name_map = {
                "system_settings": "系统设置",
                "network_connectivity": "网络",
                "hardware_info": "硬件",
                "python_environment": "Python",
                "environment_dependencies": "依赖",
                "path_validation": "路径",
                "game_settings": "游戏设置",
                "project_version": "版本",
            }

            display_name = name_map.get(result.check_name, result.check_name)

            # 格式：- 检测器名(成功/警告/错误): 问题描述
            line = f"- {display_name}({success_count}/{warning_count}/{error_count}): {issue_desc}"
            detail_lines.append(line)

        # 分段处理（每段不超过2000字符）
        briefs = []
        current_brief = header
        part_num = 1

        for line in detail_lines:
            test_brief = current_brief + "\n" + line

            if len(test_brief) > 2000:
                # 当前段已满，保存并开始新段
                briefs.append(current_brief)
                part_num += 1
                current_brief = (
                    f"OOPS_v{oops_version}, {project_short} (续{part_num})\n{line}"
                )
            else:
                current_brief = test_brief

        # 添加最后一段
        if current_brief:
            briefs.append(current_brief)

        return briefs

    @staticmethod
    def _shorten_project_name(project_name: str) -> str:
        """简化项目名称"""
        name_map = {
            "zenless_zone_zero": "Zenless_OD",
            "generic_python": "Python项目",
        }
        return name_map.get(project_name, project_name)

    @staticmethod
    def _get_check_stats(result: Any) -> Dict[str, int]:
        """获取检测项的统计信息（成功/警告/错误数量）"""
        stats = {"success": 0, "warning": 0, "error": 0}

        details = result.details
        if not details:
            # 根据 severity 判断
            if result.severity.value == "error":
                stats["error"] = 1
            elif result.severity.value == "warning":
                stats["warning"] = 1
            else:
                stats["success"] = 1
            return stats

        # 特殊处理：environment_dependencies 有子项状态
        if result.check_name == "environment_dependencies":
            for key, value in details.items():
                if isinstance(value, dict) and "status" in value:
                    status = value.get("status")
                    if status == "success":
                        stats["success"] += 1
                    elif status == "warning":
                        stats["warning"] += 1
                    elif status == "error":
                        stats["error"] += 1
            return stats

        # 从 details 中提取统计
        issues = details.get("issues", [])
        warnings = details.get("warnings", [])

        stats["error"] = len(issues)
        stats["warning"] = len(warnings)

        # 成功数量需要根据具体检测器计算
        if result.severity.value == "info" and not issues and not warnings:
            stats["success"] = 1
        elif result.severity.value == "warning" and warnings:
            # 有警告但没有错误，可能有部分成功
            stats["success"] = 1
        elif result.severity.value != "error" and not issues:
            # 没有错误，有部分成功
            stats["success"] = 1

        return stats

    @staticmethod
    def _get_issue_description(result: Any) -> str:
        """获取问题的简短描述"""
        details = result.details

        # 特殊处理：环境依赖检测
        if result.check_name == "environment_dependencies":
            if details:
                # 检查子项状态
                venv_status = details.get("virtual_environment", {})
                if venv_status.get("status") == "warning":
                    return "未使用虚拟环境"

                # 检查是否有失败项
                failed_items = []
                for key, value in details.items():
                    if isinstance(value, dict) and value.get("status") == "error":
                        failed_items.append(key)

                if failed_items:
                    return f"{len(failed_items)}项失败"

                # 检查警告项
                warning_items = []
                for key, value in details.items():
                    if isinstance(value, dict) and value.get("status") == "warning":
                        warning_items.append(key)

                if warning_items:
                    return f"{len(warning_items)}项警告"

                return "检测通过"
            return "检测完成"

        # 特殊处理：网络连通性
        if result.check_name == "network_connectivity":
            if details:
                issues = details.get("issues", [])
                if issues:
                    # 统计失败的连接
                    failed_count = len(
                        [
                            i
                            for i in issues
                            if "失败" in i or "超时" in i or "Cannot" in i
                        ]
                    )
                    if failed_count > 0:
                        return f"{failed_count}个连接失败"
            return "网络检测完成"

        # 特殊处理：Python 环境
        if result.check_name == "python_environment":
            if details:
                warnings = details.get("warnings", [])
                if warnings and any("虚拟环境" in w for w in warnings):
                    return "未检测到虚拟环境"
            return "Python环境正常"

        # 优先从 issues 和 warnings 中提取
        if details:
            issues = details.get("issues", [])
            warnings = details.get("warnings", [])

            if issues:
                # 取第一个错误的关键信息
                first_issue = issues[0]
                if len(first_issue) > 30:
                    return first_issue[:30] + "..."
                return first_issue
            elif warnings:
                # 取第一个警告的关键信息
                first_warning = warnings[0]
                if len(first_warning) > 30:
                    return first_warning[:30] + "..."
                return first_warning

        # 从 message 中提取关键信息
        message = result.message

        if "管理员" in message:
            return "未以管理员权限运行"
        elif "HDD" in message or "硬盘" in message:
            return "当前使用 HDD 硬盘，建议使用 SSD"
        elif "网络" in message and "失败" in message:
            return "网络连接失败"
        elif "虚拟环境" in message:
            return "未检测到虚拟环境"
        elif "版本" in message and "不一致" in message:
            return "版本不一致"
        elif "路径" in message:
            return "路径配置问题"
        else:
            # 截取前30个字符
            if len(message) > 30:
                return message[:30] + "..."
            return message

    @staticmethod
    def generate_markdown_brief(
        project_name: str,
        summary: Dict[str, Any],
        results: List[Any],
        system_info: Dict[str, Any],
        report_path: str = "",
    ) -> str:
        """生成 Markdown 格式简报（适合 GitHub/Gitee Issue）"""
        lines = []

        lines.append(f"## OOPS 检测报告 - {project_name}")
        lines.append("")

        # 成功率
        total = summary.get("total_checks", 0)
        completed = summary.get("completed", 0)
        success_rate = summary.get("success_rate", 0)
        lines.append(f"**成功率**: {success_rate}% ({completed}/{total}项通过)")
        lines.append("")

        # 问题列表
        errors = []
        warnings = []

        for result in results:
            if result.severity.value == "error":
                msg = BriefReportGenerator._format_issue(result)
                if msg:
                    errors.append(msg)
            elif result.severity.value == "warning":
                msg = BriefReportGenerator._format_issue(result)
                if msg:
                    warnings.append(msg)

        if errors:
            lines.append("### ❌ 错误")
            for error in errors[:3]:
                lines.append(f"- {error}")
            lines.append("")

        if warnings:
            lines.append("### ⚠️ 警告")
            for warning in warnings[:3]:
                lines.append(f"- {warning}")
            lines.append("")

        # 系统信息
        lines.append("### 📊 系统信息")
        sys_brief = BriefReportGenerator._format_system_brief(system_info)
        if sys_brief:
            lines.append(f"- {sys_brief}")

        # 版本信息
        version_brief = BriefReportGenerator._format_version_brief(results)
        if version_brief:
            lines.append(f"- 版本: {version_brief}")

        lines.append("")

        # 完整报告
        if report_path:
            lines.append(f"[查看完整报告]({report_path})")

        return "\n".join(lines)

    @staticmethod
    def generate_bbcode_brief(
        project_name: str,
        summary: Dict[str, Any],
        results: List[Any],
        system_info: Dict[str, Any],
        report_path: str = "",
    ) -> str:
        """生成 BBCode 格式简报（适合论坛）"""
        lines = []

        lines.append(f"[b]【OOPS检测报告】{project_name}[/b]")
        lines.append("")

        # 成功率
        total = summary.get("total_checks", 0)
        completed = summary.get("completed", 0)
        success_rate = summary.get("success_rate", 0)
        lines.append(
            f"[color=green]✅ 成功率: {success_rate}% ({completed}/{total}项通过)[/color]"
        )

        # 问题
        errors = []
        warnings = []

        for result in results:
            if result.severity.value == "error":
                msg = BriefReportGenerator._format_issue(result)
                if msg:
                    errors.append(msg)
            elif result.severity.value == "warning":
                msg = BriefReportGenerator._format_issue(result)
                if msg:
                    warnings.append(msg)

        for error in errors[:2]:
            lines.append(f"[color=red]❌ {error}[/color]")

        for warning in warnings[:2]:
            lines.append(f"[color=orange]⚠️ {warning}[/color]")

        # 系统信息
        sys_brief = BriefReportGenerator._format_system_brief(system_info)
        if sys_brief:
            lines.append(f"📊 {sys_brief}")

        # 完整报告
        if report_path:
            lines.append(f"[url={report_path}]查看完整报告[/url]")

        return "\n".join(lines)

    @staticmethod
    def _format_issue(result: Any) -> str:
        """格式化单个问题"""
        check_name = result.check_name
        message = result.message

        # 简化检测器名称
        name_map = {
            "system_settings": "系统设置",
            "network_connectivity": "网络连通",
            "hardware_info": "硬件",
            "python_environment": "Python环境",
            "environment_dependencies": "环境依赖",
            "path_validation": "路径",
            "game_settings": "游戏设置",
            "project_version": "版本",
        }

        display_name = name_map.get(check_name, check_name)

        # 简化消息（提取关键信息）
        if "管理员" in message:
            brief_msg = "未以管理员运行"
        elif "网络" in message and "失败" in message:
            brief_msg = "网络连接失败"
        elif "HDD" in message or "硬盘" in message:
            brief_msg = "使用HDD建议换SSD"
        elif "版本" in message and "不一致" in message:
            brief_msg = "版本不一致"
        elif "路径" in message:
            brief_msg = "路径问题"
        else:
            # 截取前30个字符
            brief_msg = message[:30] + ("..." if len(message) > 30 else "")

        return f"{display_name}: {brief_msg}"

    @staticmethod
    def _format_system_brief(system_info: Dict[str, Any]) -> str:
        """格式化系统信息简报"""
        parts = []

        # 操作系统
        basic = system_info.get("basic", {})
        if basic.get("name"):
            os_name = basic["name"]
            if "Windows" in os_name:
                parts.append("Win10" if "10" in os_name else "Win11")

        # CPU
        python_info = system_info.get("python", {})
        processor = python_info.get("processor", "")
        if "Ryzen" in processor:
            # 提取 Ryzen 型号
            import re

            match = re.search(r"Ryzen \d+ \d+", processor)
            if match:
                parts.append(f"CPU: {match.group()}")
        elif "Intel" in processor:
            match = re.search(r"i\d-\d+", processor)
            if match:
                parts.append(f"CPU: {match.group()}")

        # 内存（从 hardware 获取）
        # 这里需要从 results 中获取，暂时跳过

        return " | ".join(parts) if parts else ""

    @staticmethod
    def _format_version_brief(results: List[Any]) -> str:
        """格式化版本信息简报"""
        for result in results:
            if result.check_name == "project_version":
                details = result.details
                if not details:
                    continue

                launcher = details.get("launcher", {})
                version_info = details.get("version", {})
                remote = version_info.get("remote", {})

                launcher_ver = launcher.get("version", "")
                remote_ver = remote.get("tag_name", "") if remote else ""

                if launcher_ver and remote_ver:
                    if launcher_ver == remote_ver:
                        return f"启动器{launcher_ver} = 远程{remote_ver} ✓"
                    else:
                        return f"启动器{launcher_ver} ≠ 远程{remote_ver} ✗"
                elif launcher_ver:
                    return f"启动器{launcher_ver}"

        return ""

    @staticmethod
    def get_brief_length(brief: str) -> int:
        """获取简报长度（字符数）"""
        return len(brief)

    @staticmethod
    def truncate_to_limit(brief: str, limit: int = 500) -> str:
        """截断简报到指定长度"""
        if len(brief) <= limit:
            return brief

        # 按行截断
        lines = brief.split("\n")
        result = []
        current_length = 0

        for line in lines:
            if current_length + len(line) + 1 > limit - 20:  # 留20字符给省略提示
                break
            result.append(line)
            current_length += len(line) + 1

        result.append("... (内容过长，已截断)")
        return "\n".join(result)
