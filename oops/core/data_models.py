"""
数据模型模块
定义标准化的检测结果数据结构
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class CheckStatus(Enum):
    """检测状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SeverityLevel(Enum):
    """严重程度"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiagnosticReport:
    """诊断报告数据模型 - 顶层结构"""

    version: str = "1.0"
    project_name: str = ""
    project_path: str = ""
    current_path: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # 摘要信息
    summary: Dict[str, Any] = field(default_factory=dict)

    # 系统信息
    system_info: Dict[str, Any] = field(default_factory=dict)

    # 检测结果
    check_results: Dict[str, Any] = field(default_factory=dict)

    # 问题分类
    issues: Dict[str, List[Dict[str, str]]] = field(
        default_factory=lambda: {"critical": [], "errors": [], "warnings": []}
    )

    # 修复建议
    fix_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def to_yaml(self) -> str:
        """转换为 YAML 字符串"""
        import yaml

        return yaml.dump(
            self.to_dict(),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        import json

        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticReport":
        """从字典创建"""
        return cls(**data)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "DiagnosticReport":
        """从 YAML 字符串创建"""
        import yaml

        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> "DiagnosticReport":
        """从 JSON 字符串创建"""
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class CheckResultData:
    """单个检测结果数据模型"""

    check_name: str
    status: str  # CheckStatus.value
    severity: str  # SeverityLevel.value
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_suggestion: str = ""
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class SystemInfoData:
    """系统信息数据模型"""

    basic: Dict[str, Any] = field(default_factory=dict)
    hardware: Dict[str, Any] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)
    display: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    def get_summary(self) -> str:
        """获取摘要信息"""
        parts = []
        if self.hardware.get("cpu_model"):
            parts.append(f"CPU: {self.hardware['cpu_model']}")
        if self.hardware.get("memory_total"):
            parts.append(f"内存: {self.hardware['memory_total']}")
        if self.storage.get("disk_type"):
            disk_icon = "⚠️" if self.storage["disk_type"] == "HDD" else "✅"
            parts.append(f"磁盘: {self.storage['disk_type']} {disk_icon}")
        if self.basic.get("os"):
            parts.append(f"系统: {self.basic['os']}")
        return " | ".join(parts) if parts else "系统信息"


def create_diagnostic_report_from_results(
    results: List[Any],  # List[CheckResult]
    project_name: str,
    project_path: str,
    summary: Dict[str, Any],
) -> DiagnosticReport:
    """从检测结果创建诊断报告数据模型"""
    from pathlib import Path

    report = DiagnosticReport(
        project_name=project_name,
        project_path=project_path,
        current_path=str(Path.cwd()),
        summary=summary,
    )

    # 提取系统信息
    for result in results:
        if result.check_name == "system_info":
            report.system_info = result.details
            break

    # 添加检测结果
    for result in results:
        if result.check_name == "system_info":
            continue  # 系统信息已单独处理

        report.check_results[result.check_name] = {
            "status": result.status.value,
            "severity": result.severity.value,
            "message": result.message,
            "details": result.details,
            "fix_suggestion": result.fix_suggestion,
        }

        # 收集问题
        from oops.core.diagnostics import SeverityLevel

        if result.severity == SeverityLevel.CRITICAL:
            report.issues["critical"].append(
                {
                    "check": result.check_name,
                    "message": result.message,
                    "suggestion": result.fix_suggestion,
                }
            )
        elif result.severity == SeverityLevel.ERROR:
            report.issues["errors"].append(
                {
                    "check": result.check_name,
                    "message": result.message,
                    "suggestion": result.fix_suggestion,
                }
            )
        elif result.severity == SeverityLevel.WARNING:
            report.issues["warnings"].append(
                {
                    "check": result.check_name,
                    "message": result.message,
                    "suggestion": result.fix_suggestion,
                }
            )

    # 提取修复建议
    for result in results:
        if result.fix_suggestion:
            report.fix_suggestions.append(
                f"{result.check_name}: {result.fix_suggestion}"
            )

    return report
