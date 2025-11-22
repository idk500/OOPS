"""
问题匹配器
基于知识库的常见问题匹配和解决方案推荐
"""

import re
from typing import Dict, List, Any, Optional


class IssueMatcher:
    """问题匹配器 - 基于知识库的常见问题"""

    def __init__(self):
        # 安装问题知识库
        self.installation_issues = {
            "WinError 10060": {
                "description": "连接时间超时",
                "solutions": [
                    "返回安装过程的上一步，卸载所选文件夹中安装的所有文件，重新安装"
                ],
                "severity": "error",
            },
            "404": {
                "description": "版本过老或程序已退出",
                "solutions": ["下载最新版本脚本", "检查程序是否正常运行"],
                "severity": "error",
            },
            "WinError 10061": {
                "description": "连接服务器被拒绝",
                "solutions": [
                    "使用管理员权限运行安装程序",
                    "关闭个人代理（如steam++，UU加速器, 雷神加速器等）",
                    "更换手机热点再试",
                    "用最新版的 FULL-ENV.zip 再次安装",
                ],
                "severity": "error",
            },
            "403": {
                "description": "连接服务器被拒绝",
                "solutions": [
                    "使用管理员权限运行安装程序",
                    "关闭个人代理",
                    "更换网络环境",
                ],
                "severity": "error",
            },
            "WinError 87": {
                "description": "参数错误",
                "solutions": [
                    "关闭杀毒软件后使用安装器检查Python文件完整性",
                    "使用管理员权限启动启动器",
                    "检查Windows版本是否支持（Win10+）",
                ],
                "severity": "error",
            },
            "os error 3": {
                "description": "路径问题",
                "solutions": [
                    "安装路径应为纯英文字符，且不含有空格",
                    "使用推荐路径: D:\\ZZZ-OD",
                ],
                "severity": "error",
            },
            "onnxruntime": {
                "description": "ONNX运行时错误",
                "solutions": [
                    "打开debug.bat，修复onnxruntime",
                    "手动安装: pip install onnxruntime==1.18.0",
                ],
                "severity": "error",
            },
            "file name too long": {
                "description": "文件路径过长",
                "solutions": ["另寻文件夹安装", "使用较短的路径名"],
                "severity": "error",
            },
            "ssl": {
                "description": "SSL证书错误",
                "solutions": [
                    "启动debug.bat修复ssl证书",
                    "配置Git SSL后端: git config --global http.sslBackend schannel",
                    "删除 Program Files/Git 整个文件夹后重新安装",
                ],
                "severity": "error",
            },
            "Darwin": {
                "description": "兼容性错误",
                "solutions": ["更换个人热点解决校园网问题"],
                "severity": "error",
            },
            "WinError 2": {
                "description": "系统找不到指定的文件",
                "solutions": [
                    "检查Powershell权限和环境是否完整",
                    "添加环境变量: C:\\Windows\\System32\\WindowsPowerShell\\v1.0",
                ],
                "severity": "error",
            },
            "PySide6": {
                "description": "界面库错误",
                "solutions": ["删除.env文件夹之后重新进行安装流程"],
                "severity": "error",
            },
            "DLL初始化例程失败": {
                "description": "依赖库缺失",
                "solutions": [
                    "安装最新版的 Microsoft Visual C++",
                    "下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe",
                ],
                "severity": "error",
            },
        }

        # 使用问题知识库
        self.usage_issues = {
            "未找到 按键-普通攻击": {
                "description": "游戏画面还在加载",
                "solutions": ["等待游戏加载完成", "确保游戏画面完整显示"],
                "severity": "warning",
            },
            "items": {
                "description": "OCR缓存问题",
                "solutions": ["打开设置-脚本环境-ocr缓存，关闭缓存"],
                "severity": "warning",
            },
            "no attribute data": {
                "description": "脚本状态异常",
                "solutions": ["重启脚本"],
                "severity": "warning",
            },
            "Python路径错误": {
                "description": "脚本路径被移动",
                "solutions": [
                    "安装完成后，绝对路径固定，不可移动脚本内容",
                    "重新安装到固定位置",
                ],
                "severity": "error",
            },
            "闪避助手操作不正常": {
                "description": "键鼠操作冲突",
                "solutions": [
                    "脚本优先执行键鼠操作，键鼠的操作可能会把脚本的操作给覆盖掉",
                    "避免在脚本运行时手动操作",
                ],
                "severity": "info",
            },
            "体力计划无法执行": {
                "description": "配置未生效",
                "solutions": ["配置好体力计划后，重启一条龙脚本"],
                "severity": "warning",
            },
            "自动战斗只会闪避": {
                "description": "战斗配置问题",
                "solutions": ["使用通用战斗配置"],
                "severity": "warning",
            },
            "自动战斗不会切人": {
                "description": "角色识别问题",
                "solutions": [
                    "尝试全屏模式开启自动战斗",
                    "保证绝区零游戏界面在前台，并关闭弹窗等遮挡",
                    "移除mod",
                    "新角色和新皮肤可能未适配，请耐心等待",
                ],
                "severity": "warning",
            },
            "空洞内交互时冲刺": {
                "description": "性能或配置问题",
                "solutions": [
                    "提高自动截图频率",
                    "换用低速/小个头角色",
                    "调高游戏分辨率",
                    "换个性能好的电脑",
                ],
                "severity": "info",
            },
        }

    def match_issue(self, error_message: str) -> Optional[Dict[str, Any]]:
        """匹配错误信息到知识库

        Args:
            error_message: 错误信息

        Returns:
            匹配到的问题信息，包含描述和解决方案
        """
        error_lower = error_message.lower()

        # 先匹配安装问题
        for keyword, issue_info in self.installation_issues.items():
            if keyword.lower() in error_lower:
                return {
                    "type": "installation",
                    "keyword": keyword,
                    "description": issue_info["description"],
                    "solutions": issue_info["solutions"],
                    "severity": issue_info["severity"],
                }

        # 再匹配使用问题
        for keyword, issue_info in self.usage_issues.items():
            if keyword.lower() in error_lower:
                return {
                    "type": "usage",
                    "keyword": keyword,
                    "description": issue_info["description"],
                    "solutions": issue_info["solutions"],
                    "severity": issue_info["severity"],
                }

        return None

    def get_all_issues_by_type(self, issue_type: str) -> Dict[str, Any]:
        """获取指定类型的所有问题"""
        if issue_type == "installation":
            return self.installation_issues
        elif issue_type == "usage":
            return self.usage_issues
        else:
            return {}

    def search_issues(self, query: str) -> List[Dict[str, Any]]:
        """搜索相关问题"""
        results = []
        query_lower = query.lower()

        # 搜索安装问题
        for keyword, issue_info in self.installation_issues.items():
            if (
                query_lower in keyword.lower()
                or query_lower in issue_info["description"].lower()
            ):
                results.append(
                    {
                        "type": "installation",
                        "keyword": keyword,
                        "description": issue_info["description"],
                        "solutions": issue_info["solutions"],
                        "severity": issue_info["severity"],
                    }
                )

        # 搜索使用问题
        for keyword, issue_info in self.usage_issues.items():
            if (
                query_lower in keyword.lower()
                or query_lower in issue_info["description"].lower()
            ):
                results.append(
                    {
                        "type": "usage",
                        "keyword": keyword,
                        "description": issue_info["description"],
                        "solutions": issue_info["solutions"],
                        "severity": issue_info["severity"],
                    }
                )

        return results


class SolutionRecommender:
    """解决方案推荐器"""

    def __init__(self):
        self.issue_matcher = IssueMatcher()

    def recommend_solutions(
        self, diagnostic_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """基于诊断结果推荐解决方案

        Args:
            diagnostic_results: 诊断结果列表

        Returns:
            推荐的解决方案列表
        """
        recommendations = []

        for result in diagnostic_results:
            # 提取错误信息
            error_message = result.get("message", "")
            error_details = result.get("details", {})

            # 匹配问题
            matched_issue = self.issue_matcher.match_issue(error_message)

            if matched_issue:
                recommendations.append(
                    {
                        "check_name": result.get("check_name", "unknown"),
                        "issue": matched_issue,
                        "priority": self._get_priority(matched_issue["severity"]),
                    }
                )

            # 检查详细信息中的错误
            for key, value in error_details.items():
                if isinstance(value, dict) and value.get("status") == "error":
                    error_msg = value.get("message", "") or value.get("error", "")
                    matched = self.issue_matcher.match_issue(error_msg)
                    if matched:
                        recommendations.append(
                            {
                                "check_name": f"{result.get('check_name', 'unknown')}.{key}",
                                "issue": matched,
                                "priority": self._get_priority(matched["severity"]),
                            }
                        )

        # 按优先级排序
        recommendations.sort(key=lambda x: x["priority"], reverse=True)

        return recommendations

    def _get_priority(self, severity: str) -> int:
        """获取优先级分数"""
        priority_map = {"error": 3, "warning": 2, "info": 1}
        return priority_map.get(severity, 0)

    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """格式化推荐信息为可读文本"""
        if not recommendations:
            return "未发现已知问题，所有检测正常。"

        output = []
        output.append("=" * 60)
        output.append("基于知识库的解决方案推荐")
        output.append("=" * 60)
        output.append("")

        for i, rec in enumerate(recommendations, 1):
            issue = rec["issue"]
            output.append(f"{i}. 【{issue['severity'].upper()}】 {issue['keyword']}")
            output.append(f"   检测项: {rec['check_name']}")
            output.append(f"   问题描述: {issue['description']}")
            output.append(f"   解决方案:")
            for j, solution in enumerate(issue["solutions"], 1):
                output.append(f"      {j}) {solution}")
            output.append("")

        return "\n".join(output)
