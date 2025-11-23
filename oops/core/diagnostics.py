"""
诊断套件模块
负责协调和执行各种检测规则，管理检测流程和结果收集
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from oops.core.config import ConfigManager, DetectionRule

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """检测状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SeverityLevel(Enum):
    """问题严重程度枚举"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CheckResult:
    """检测结果数据类"""

    check_name: str
    status: CheckStatus
    severity: SeverityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_suggestion: str = ""
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class DiagnosticSuite:
    """诊断套件 - 核心检测协调器"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.results: List[CheckResult] = []
        self.detection_rules: Dict[str, DetectionRule] = {}
        self.is_running = False

        # 注册内置检测规则
        self._register_default_rules()

    def _register_default_rules(self):
        """注册默认检测规则"""
        from oops.detectors.environment import EnvironmentDependencyDetector
        from oops.detectors.network import NetworkConnectivityDetector
        from oops.detectors.paths import PathValidationDetector
        from oops.detectors.system_info import SystemInfoDetector

        self.detection_rules = {
            "system_info": SystemInfoDetector(),
            "network_connectivity": NetworkConnectivityDetector(),
            "environment_dependencies": EnvironmentDependencyDetector(),
            "path_validation": PathValidationDetector(),
        }

    async def run_diagnostics(
        self, project_name: str, selected_checks: Optional[List[str]] = None
    ) -> List[CheckResult]:
        """运行诊断检测"""
        self.is_running = True
        self.results.clear()

        logger.info(f"开始为项目 {project_name} 运行诊断检测")

        # 加载项目配置
        project_config = self.config_manager.get_project_config(project_name)
        if not project_config:
            error_result = CheckResult(
                check_name="config_loading",
                status=CheckStatus.FAILED,
                severity=SeverityLevel.ERROR,
                message=f"无法加载项目配置: {project_name}",
                fix_suggestion="请检查项目配置文件是否存在且格式正确",
            )
            self.results.append(error_result)
            self.is_running = False
            return self.results

        # 验证配置
        if not self.config_manager.validate_config(project_config):
            error_result = CheckResult(
                check_name="config_validation",
                status=CheckStatus.FAILED,
                severity=SeverityLevel.ERROR,
                message="项目配置验证失败",
                fix_suggestion="请检查项目配置文件的必需字段",
            )
            self.results.append(error_result)
            self.is_running = False
            return self.results

        # 确定要运行的检测
        checks_to_run = self._determine_checks_to_run(project_config, selected_checks)

        # 显示将要执行的检测项目
        self._show_detection_plan(checks_to_run, project_config)

        # 并行运行检测
        tasks = []
        for check_name in checks_to_run:
            if check_name in self.detection_rules:
                task = self._run_single_check(
                    check_name, self.detection_rules[check_name], project_config
                )
                tasks.append(task)

        # 等待所有检测完成
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.is_running = False
        logger.info(f"诊断检测完成，共执行 {len(self.results)} 项检测")
        return self.results

    def _show_detection_plan(
        self, checks_to_run: List[str], project_config: Dict[str, Any]
    ):
        """显示检测计划 - 简化显示"""
        checks_config = project_config.get("checks", {})

        print("[*] 检测项目计划:")
        print("   +- 基础检测")

        # 网络检测
        if "network_connectivity" in checks_to_run:
            network_config = checks_config.get("network", {})
            git_count = len(network_config.get("git_repos", []))
            pypi_count = len(network_config.get("pypi_sources", []))
            print(f"   +- 网络连通性 ({git_count}个Git仓库, {pypi_count}个PyPI源)")

        # 环境检测
        if "environment_dependencies" in checks_to_run:
            env_config = checks_config.get("environment", {})
            python_ver = env_config.get("python_version", ">=3.8")
            lib_count = len(env_config.get("system_libraries", []))
            print(f"   +- 环境依赖 (Python{python_ver}, {lib_count}个系统库)")

        # 路径检测
        if "path_validation" in checks_to_run:
            paths_config = checks_config.get("paths", {})
            install_path = (
                project_config.get("project", {})
                .get("paths", {})
                .get("install_path", "未设置")
            )
            print(f"   +- 路径规范 (安装路径: {install_path})")

        print("   +- 检测准备完成")
        print()

    def _determine_checks_to_run(
        self, project_config: Dict[str, Any], selected_checks: Optional[List[str]]
    ) -> List[str]:
        """确定需要运行的检测项目"""
        if selected_checks:
            return [check for check in selected_checks if check in self.detection_rules]

        # 根据配置确定启用的检测
        enabled_checks = []
        checks_config = project_config.get("checks", {})

        for check_category, category_config in checks_config.items():
            if category_config.get("enabled", False):
                # 将分类映射到具体的检测规则
                if check_category == "system_info":
                    enabled_checks.append("system_info")
                elif check_category == "network":
                    enabled_checks.append("network_connectivity")
                elif check_category == "environment":
                    enabled_checks.append("environment_dependencies")
                elif check_category == "paths":
                    enabled_checks.append("path_validation")
                # 可以继续添加其他分类映射

        return enabled_checks

    async def _run_single_check(
        self, check_name: str, rule: DetectionRule, project_config: Dict[str, Any]
    ):
        """运行单个检测"""
        logger.info(f"开始执行检测: {check_name}")

        start_time = datetime.now()
        result = CheckResult(
            check_name=check_name,
            status=CheckStatus.RUNNING,
            severity=SeverityLevel.INFO,
            message="检测进行中...",
        )
        self.results.append(result)

        try:
            # 为环境检测动态添加 project_path
            if check_name == "environment_dependencies":
                install_path = (
                    project_config.get("project", {})
                    .get("paths", {})
                    .get("install_path", "")
                )
                if install_path and "checks" in project_config:
                    if "environment" not in project_config["checks"]:
                        project_config["checks"]["environment"] = {}
                    project_config["checks"]["environment"][
                        "project_path"
                    ] = install_path
                    logger.debug(f"为环境检测设置项目路径: {install_path}")

            # 执行检测规则
            check_result = await asyncio.get_event_loop().run_in_executor(
                None, rule.check, project_config
            )

            # 更新检测结果
            result.status = CheckStatus.COMPLETED
            result.message = check_result.get("message", "检测完成")
            result.details = check_result.get("details", {})
            result.fix_suggestion = rule.get_fix_suggestion(check_result)
            result.execution_time = (datetime.now() - start_time).total_seconds()

            # 根据检测结果设置严重程度
            if check_result.get("status") == "error":
                result.severity = SeverityLevel.ERROR
            elif check_result.get("status") == "warning":
                result.severity = SeverityLevel.WARNING
            elif check_result.get("status") == "critical":
                result.severity = SeverityLevel.CRITICAL
            else:
                result.severity = SeverityLevel.INFO

            # 特殊处理：从system_info中提取硬件适配信息作为独立检测项
            if check_name == "system_info":
                self._create_hardware_compatibility_result(check_result, start_time)

            logger.info(f"检测完成: {check_name} - {result.message}")

        except Exception as e:
            logger.error(f"检测执行失败 {check_name}: {e}")
            result.status = CheckStatus.FAILED
            result.severity = SeverityLevel.ERROR
            result.message = f"检测执行失败: {str(e)}"
            result.execution_time = (datetime.now() - start_time).total_seconds()

    def _create_hardware_compatibility_result(
        self, system_info_result: Dict[str, Any], start_time: datetime
    ):
        """从系统信息中创建硬件适配检测结果"""
        details = system_info_result.get("details", {})
        validation = details.get("validation", {})

        if not validation:
            return

        # 收集硬件适配问题
        issues = []
        warnings = []
        recommendations = []
        has_error = False
        has_warning = False

        # 内存验证
        if "memory" in validation:
            mem_val = validation["memory"]
            if not mem_val.get("valid"):
                issues.append(f"内存: {mem_val.get('message', '不符合要求')}")
                if mem_val.get("recommendation"):
                    recommendations.append(mem_val["recommendation"])
                has_error = True

        # 磁盘类型验证
        if "disk_type" in validation:
            disk_val = validation["disk_type"]
            if disk_val.get("warning"):
                warnings.append(f"磁盘类型: {disk_val.get('message', 'HDD性能较低')}")
                if disk_val.get("recommendation"):
                    recommendations.append(disk_val["recommendation"])
                has_warning = True

        # 用户名验证
        if "username" in validation:
            user_val = validation["username"]
            if not user_val.get("valid"):
                issues.append(f"用户名: {user_val.get('message', '不符合规范')}")
                has_error = True
            elif user_val.get("warnings"):
                warnings.append(f"用户名: {user_val.get('message', '存在潜在问题')}")
                has_warning = True
            if user_val.get("recommendations"):
                recommendations.extend(user_val["recommendations"])

        # 显示设置验证
        if "display_settings" in validation:
            display_val = validation["display_settings"]
            if not display_val.get("valid"):
                display_issues = display_val.get("issues", [])
                issues.extend([f"显示设置: {issue}" for issue in display_issues])
                has_error = True
            elif display_val.get("warning"):
                display_warnings = display_val.get("warnings", [])
                warnings.extend(
                    [f"显示设置: {warning}" for warning in display_warnings]
                )
                has_warning = True
            if display_val.get("recommendations"):
                recommendations.extend(display_val["recommendations"])

        # 只有在有问题时才创建硬件适配检测结果
        if issues or warnings:
            # 确定状态和严重程度
            if has_error:
                status = "error"
                severity = SeverityLevel.ERROR
                message = f"硬件适配检测发现 {len(issues)} 个问题"
            elif has_warning:
                status = "warning"
                severity = SeverityLevel.WARNING
                message = f"硬件适配检测发现 {len(warnings)} 个警告"
            else:
                status = "success"
                severity = SeverityLevel.INFO
                message = "硬件适配检测通过"

            # 创建检测结果
            hardware_result = CheckResult(
                check_name="hardware_compatibility",
                status=CheckStatus.COMPLETED,
                severity=severity,
                message=message,
                details={
                    "issues": issues,
                    "warnings": warnings,
                    "validation": validation,
                },
                fix_suggestion="; ".join(recommendations) if recommendations else "",
                execution_time=(datetime.now() - start_time).total_seconds(),
            )

            self.results.append(hardware_result)
            logger.info(f"创建硬件适配检测结果: {message}")

    def get_summary(self) -> Dict[str, Any]:
        """获取检测摘要"""
        if not self.results:
            return {
                "total_checks": 0,
                "completed": 0,
                "failed": 0,
                "critical_issues": 0,
                "error_issues": 0,
                "warning_issues": 0,
            }

        total = len(self.results)
        completed = len([r for r in self.results if r.status == CheckStatus.COMPLETED])
        failed = len([r for r in self.results if r.status == CheckStatus.FAILED])

        # 统计问题严重程度
        critical_issues = len(
            [r for r in self.results if r.severity == SeverityLevel.CRITICAL]
        )
        error_issues = len(
            [r for r in self.results if r.severity == SeverityLevel.ERROR]
        )
        warning_issues = len(
            [r for r in self.results if r.severity == SeverityLevel.WARNING]
        )

        return {
            "total_checks": total,
            "completed": completed,
            "failed": failed,
            "critical_issues": critical_issues,
            "error_issues": error_issues,
            "warning_issues": warning_issues,
            "success_rate": (completed / total * 100) if total > 0 else 0,
        }

    def get_results_by_severity(self, severity: SeverityLevel) -> List[CheckResult]:
        """按严重程度筛选检测结果"""
        return [result for result in self.results if result.severity == severity]

    def get_failed_checks(self) -> List[CheckResult]:
        """获取失败的检测"""
        return [
            result for result in self.results if result.status == CheckStatus.FAILED
        ]

    def clear_results(self):
        """清空检测结果"""
        self.results.clear()


class QuickDiagnosticSuite(DiagnosticSuite):
    """快速诊断套件 - 用于快速扫描"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager)

    async def run_quick_scan(self, project_name: str) -> List[CheckResult]:
        """运行快速扫描 - 只执行关键检测"""
        critical_checks = ["network_connectivity", "environment_dependencies"]
        return await self.run_diagnostics(project_name, critical_checks)


class FullDiagnosticSuite(DiagnosticSuite):
    """完整诊断套件 - 执行所有可用检测"""

    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager)

    async def run_full_scan(self, project_name: str) -> List[CheckResult]:
        """运行完整扫描 - 执行所有检测"""
        all_checks = list(self.detection_rules.keys())
        return await self.run_diagnostics(project_name, all_checks)
