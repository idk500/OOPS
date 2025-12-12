#!/usr/bin/env python3
"""
OOPS 主程序入口
一键运行预检系统 - One-click Operating Pre-check System

让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly
"""

import argparse
import asyncio
import logging
import sys
import webbrowser
from pathlib import Path

from oops.core.config import ConfigManager
from oops.core.diagnostics import (
    DiagnosticSuite,
    QuickDiagnosticSuite,
    FullDiagnosticSuite,
)
from oops.core.report import ReportManager


def setup_logging(verbose: bool = False):
    """设置日志"""
    log_level = logging.DEBUG if verbose else logging.INFO

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 文件处理器 - 记录所有日志
    file_handler = logging.FileHandler("oops.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # 控制台处理器 - 只在verbose模式下显示详细日志
    console_handler = logging.StreamHandler(sys.stdout)
    if verbose:
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        # 非verbose模式下，只显示WARNING及以上级别
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    # 清除现有处理器并添加新的
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="OOPS - 一键运行预检系统 | 让游戏脚本运行更顺畅",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  oops.py                               # 交互式选择项目
  oops.py --project zenless_zone_zero   # 检测指定项目
  oops.py --quick-scan                  # 快速扫描所有启用项目
  oops.py --full-scan                   # 完整扫描所有启用项目
  oops.py --list-projects               # 列出所有可用项目
  oops.py --create-config               # 创建默认配置文件
        """,
    )

    # 项目选择
    project_group = parser.add_argument_group("项目选择")
    project_group.add_argument("--project", "-p", type=str, help="指定要检测的项目名称")
    project_group.add_argument(
        "--list-projects", "-l", action="store_true", help="列出所有可用项目"
    )

    # 检测模式
    mode_group = parser.add_argument_group("检测模式")
    mode_group.add_argument(
        "--quick-scan", "-q", action="store_true", help="快速扫描模式（仅关键检测）"
    )
    mode_group.add_argument(
        "--full-scan", "-f", action="store_true", help="完整扫描模式（所有检测）"
    )

    # 输出选项
    output_group = parser.add_argument_group("输出选项")
    output_group.add_argument(
        "--report-format",
        choices=["html", "json", "markdown", "all"],
        default="html",
        help="报告格式（默认: html）",
    )
    output_group.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="reports",
        help="报告输出目录（默认: reports）",
    )
    output_group.add_argument(
        "--no-report", action="store_true", help="不生成报告文件，仅输出到控制台"
    )

    # 配置选项
    config_group = parser.add_argument_group("配置选项")
    config_group.add_argument(
        "--config-dir",
        "-c",
        type=str,
        default="configs",
        help="配置文件目录（默认: configs）",
    )
    config_group.add_argument(
        "--create-config", action="store_true", help="创建默认配置文件"
    )

    # 其他选项
    other_group = parser.add_argument_group("其他选项")
    other_group.add_argument(
        "--verbose", "-v", action="store_true", help="详细输出模式"
    )
    other_group.add_argument(
        "--no-browser", action="store_true", help="不自动在浏览器中打开HTML报告"
    )
    other_group.add_argument("--version", action="store_true", help="显示版本信息")

    return parser.parse_args()


def show_version():
    """显示版本信息"""
    from oops import __version__

    print(f"OOPS - 一键运行预检系统 v{__version__}")
    print("One-click Operating Pre-check System")
    print()
    print("让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly")
    print()
    print("https://github.com/idk500/OOPS")
    sys.exit(0)


def list_projects(config_manager: ConfigManager):
    """列出所有项目"""
    if not config_manager.load_master_config():
        print("[ERROR] 无法加载主配置文件")
        return

    projects = config_manager.get_enabled_projects()
    if not projects:
        print("[INFO] 没有找到启用的项目")
        return

    print("[*] 可用项目列表:")
    for i, project_name in enumerate(projects, 1):
        project_config = config_manager.get_project_config(project_name)
        if project_config:
            # 优先从顶层 project_name 获取，如果没有则从 project.name 获取
            name = project_config.get("project_name") or project_config.get(
                "project", {}
            ).get("name", project_name)
            project_info = project_config.get("project", {})
            description = project_info.get("description", "暂无描述")
            print(f"  {i}. {name} ({project_name})")
            print(f"     {description}")
        else:
            print(f"  {i}. {project_name} (配置加载失败)")
        print()


def create_default_configs(config_dir: str):
    """创建默认配置文件"""
    from oops.core.config import create_default_master_config, ConfigManager
    import yaml

    config_path = Path(config_dir)
    config_path.mkdir(exist_ok=True)

    # 创建主配置文件
    master_config = create_default_master_config()
    master_config_path = config_path / "oops_master.yaml"

    with open(master_config_path, "w", encoding="utf-8") as f:
        yaml.dump(master_config, f, allow_unicode=True, indent=2)

    print(f"✅ 已创建主配置文件: {master_config_path}")

    # 创建项目配置文件模板
    config_manager = ConfigManager(config_dir)
    default_config = config_manager.create_default_config()

    # 绝区零一条龙配置
    zzz_config = default_config.copy()
    zzz_config["project"] = {
        "name": "绝区零一条龙",
        "type": "game_script",
        "description": "绝区零自动化脚本",
        "paths": {"install_path": "D:/ZZZ-OD", "config_path": "D:/ZZZ-OD/config"},
    }
    # 项目特定的Git仓库（会添加到默认列表）
    zzz_config["checks"]["network"]["git_repos"] = [
        "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"
    ]
    # PyPI源使用默认配置（在 defaults.yaml 中定义）
    # 如需自定义，取消下面的注释：
    # zzz_config['checks']['network']['pypi_sources'] = [
    #     'https://pypi.org/simple/',
    #     'https://pypi.tuna.tsinghua.edu.cn/simple/'
    # ]

    zzz_config_path = config_path / "zenless_zone_zero.yaml"
    with open(zzz_config_path, "w", encoding="utf-8") as f:
        yaml.dump(zzz_config, f, allow_unicode=True, indent=2)
    print(f"✅ 已创建项目配置: {zzz_config_path}")

    # 通用Python项目配置
    generic_config = default_config.copy()
    generic_config["project"] = {
        "name": "通用Python项目",
        "type": "generic",
        "description": "通用Python项目检测模板",
    }

    generic_config_path = config_path / "generic_python.yaml"
    with open(generic_config_path, "w", encoding="utf-8") as f:
        yaml.dump(generic_config, f, allow_unicode=True, indent=2)
    print(f"✅ 已创建项目配置: {generic_config_path}")

    print("\n🎉 默认配置文件创建完成！")
    print("💡 请根据实际需求修改配置文件中的路径和设置")


async def display_diagnostic_results(
    results, summary, diagnostic_suite, args, project_name, config_manager=None
):
    """显示诊断结果的通用函数"""
    # 显示简化摘要信息
    print(f"\n[*] 检测完成!")
    print(f"   [+] 成功: {summary['completed']} 项")
    print(f"   [-] 失败: {summary['failed']} 项")
    print(f"   [~] 跳过: {summary.get('skipped', 0)} 项")
    total_issues = (
        summary["critical_issues"] + summary["error_issues"] + summary["warning_issues"]
    )
    print(f"   [!] 问题: {total_issues} 个")
    print(f"   [%] 成功率: {summary['success_rate']:.1f}%")

    # 合并显示所有问题（按严重程度排序）
    from oops.core.diagnostics import SeverityLevel

    all_issues = []
    all_issues.extend(diagnostic_suite.get_results_by_severity(SeverityLevel.CRITICAL))
    all_issues.extend(diagnostic_suite.get_results_by_severity(SeverityLevel.ERROR))
    all_issues.extend(diagnostic_suite.get_results_by_severity(SeverityLevel.WARNING))

    if all_issues:
        print(f"\n{'='*60}")
        print(f"发现 {total_issues} 个需要关注的问题")
        print(f"{'='*60}")

        for i, result in enumerate(all_issues, 1):
            severity_icon = {
                "critical": "🔴",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
            }.get(result.severity.value, "❓")

            severity_text = {
                "critical": "严重",
                "error": "错误",
                "warning": "警告",
                "info": "信息",
            }.get(result.severity.value, "未知")

            print(f"\n{i}. {severity_icon} [{severity_text}] {result.check_name}")

            # 显示详细信息
            if result.details:
                # 提取具体失败的检测项
                failed_items = []
                for key, value in result.details.items():
                    if isinstance(value, dict):
                        if value.get("status") in ["error", "failure", "timeout"]:
                            error_msg = value.get("error", value.get("message", ""))
                            failed_items.append(f"   • {key}: {error_msg}")

                if failed_items:
                    print("   具体问题:")
                    for item in failed_items[:3]:  # 最多显示3个
                        print(item)
                    if len(failed_items) > 3:
                        print(f"   ... 还有 {len(failed_items) - 3} 个问题")
            else:
                # 显示主要消息
                simple_message = (
                    result.message.split("\n")[0]
                    if "\n" in result.message
                    else result.message
                )
                print(f"   {simple_message}")

            # 显示修复建议
            if result.fix_suggestion:
                print(f"   💡 建议: {result.fix_suggestion}")

        print(f"\n{'='*60}")
        print(f"💡 详细信息请查看HTML报告")
        print(f"{'='*60}")

    # 基于知识库推荐解决方案
    try:
        from oops.knowledge import SolutionRecommender

        recommender = SolutionRecommender()

        # 转换结果格式
        results_for_recommendation = []
        for result in results:
            results_for_recommendation.append(
                {
                    "check_name": result.check_name,
                    "message": result.message,
                    "details": result.details,
                    "severity": result.severity.value,
                }
            )

        recommendations = recommender.recommend_solutions(results_for_recommendation)

        if recommendations and args.verbose:
            print("\n" + recommender.format_recommendations(recommendations))
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.debug(f"解决方案推荐失败: {e}")

    # 生成报告 - 默认同时生成 HTML 和 YAML
    if not args.no_report:
        from oops.core.report import ReportGenerator, ReportConfig

        # 获取项目配置（用于报告中的项目名称显示）
        project_config = None
        if config_manager:
            project_config = config_manager.get_project_config(
                project_name, silent=True
            )

        yaml_path = None

        # 先生成 YAML 报告（用于提交给开发者）
        try:
            yaml_config = ReportConfig(
                format="yaml", output_dir=args.output_dir, include_timestamp=True
            )
            yaml_generator = ReportGenerator(yaml_config)
            yaml_content = yaml_generator.generate_report(
                results, project_name, summary, project_config=project_config
            )
            yaml_path = yaml_generator.save_report(yaml_content, project_name)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"YAML 报告生成失败: {e}")
            import traceback

            traceback.print_exc()

        # 生成 HTML 报告（用于用户查看），传入 YAML 路径
        html_config = ReportConfig(
            format="html", output_dir=args.output_dir, include_timestamp=True
        )
        html_generator = ReportGenerator(html_config)
        # 将 YAML 路径传递给 HTML 报告
        yaml_abs_path = str(Path(yaml_path).absolute()) if yaml_path else ""
        html_content = html_generator.generate_report(
            results,
            project_name,
            summary,
            yaml_path=yaml_abs_path,
            project_config=project_config,
        )
        html_path = html_generator.save_report(html_content, project_name)

        print(f"\n📄 HTML报告已生成: {html_path}")
        if yaml_path:
            print(f"📄 YAML报告已生成: {yaml_path}")
            print(f"💡 提示: 将 YAML 报告提交给项目开发者以获取支持")
        else:
            print(f"⚠️  YAML报告生成失败，请查看日志")

        # 自动打开HTML报告（除非用户禁用）
        if not args.no_browser:
            try:
                webbrowser.open(f"file://{Path(html_path).absolute()}")
                print(f"🌐 已在浏览器中打开报告")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.debug(f"无法自动打开浏览器: {e}")


async def run_diagnostic_for_project(
    project_name: str, args, config_manager: ConfigManager
):
    """为指定项目运行诊断"""
    logger = logging.getLogger(__name__)

    print(f"[*] 开始检测项目: {project_name}")

    # 选择诊断套件
    if args.quick_scan:
        diagnostic_suite = QuickDiagnosticSuite(config_manager)
        results = await diagnostic_suite.run_quick_scan(project_name)
    elif args.full_scan:
        diagnostic_suite = FullDiagnosticSuite(config_manager)
        results = await diagnostic_suite.run_full_scan(project_name)
    else:
        diagnostic_suite = DiagnosticSuite(config_manager)
        results = await diagnostic_suite.run_diagnostics(project_name)

    # 获取摘要
    summary = diagnostic_suite.get_summary()

    # 使用通用显示函数
    await display_diagnostic_results(
        results, summary, diagnostic_suite, args, project_name, config_manager
    )

    return summary


async def interactive_project_selection(args, config_manager: ConfigManager):
    """交互式项目选择"""

    # 尝试自动检测当前目录的项目
    from oops.core.project_detector import ProjectDetector

    detector = ProjectDetector()

    detected_project = detector.detect_current_directory()
    if not detected_project:
        # 尝试扫描父目录
        detected_project = detector.scan_parent_directories()

    if detected_project:
        from pathlib import Path

        print(f"[*] 🎯 自动检测到项目: {detected_project['project_name']}")
        print(f"[*] 📁 项目路径: {detected_project['install_path']}")
        print(f"[*] 📍 当前运行路径: {Path.cwd()}")
        print()

        # 使用检测到的配置运行诊断
        print(f"[*] 🚀 开始自动诊断...")

        # 加载项目配置并注入检测到的路径
        project_config = config_manager.get_project_config(
            detected_project["project_id"]
        )
        if project_config:
            # 注入检测到的安装路径
            if "project" not in project_config:
                project_config["project"] = {}
            if "paths" not in project_config["project"]:
                project_config["project"]["paths"] = {}
            project_config["project"]["paths"]["install_path"] = detected_project[
                "install_path"
            ]

            # 更新配置管理器中的配置
            config_manager.project_configs[detected_project["project_id"]] = (
                project_config
            )

        # 创建临时配置管理器
        from oops.core.diagnostics import DiagnosticSuite

        diagnostic_suite = DiagnosticSuite(config_manager)

        # 直接使用检测到的配置运行
        results = await diagnostic_suite.run_diagnostics(detected_project["project_id"])

        # 获取摘要
        summary = diagnostic_suite.get_summary()

        # 显示结果
        await display_diagnostic_results(
            results,
            summary,
            diagnostic_suite,
            args,
            detected_project["project_id"],
            config_manager,
        )
        return

    # 如果没有检测到项目，使用原有逻辑
    if not config_manager.load_master_config():
        print("[ERROR] 无法加载主配置文件")
        return

    # 只获取配置成功的项目（静默加载，不显示警告）
    valid_projects = []
    projects = config_manager.get_enabled_projects()

    for project_name in projects:
        project_config = config_manager.get_project_config(project_name, silent=True)
        if project_config:
            valid_projects.append((project_name, project_config))

    if not valid_projects:
        print("[INFO] 没有找到有效的项目配置")
        print("[*] 💡 提示: 将 oops.exe 放到项目根目录可以自动检测")
        return

    # 自动模式：直接运行所有有效项目，无需用户输入
    print(f"[*] 🚀 自动模式：检测到 {len(valid_projects)} 个可用项目")
    print(f"[*] 💡 提示：使用 --project 参数可以指定单个项目")
    print()

    # 依次检测所有有效项目
    for i, (project_name, project_config) in enumerate(valid_projects, 1):
        # 优先从顶层 project_name 获取，如果没有则从 project.name 获取
        name = project_config.get("project_name") or project_config.get(
            "project", {}
        ).get("name", project_name)

        if len(valid_projects) > 1:
            print(f"\n{'='*60}")
            print(f"[{i}/{len(valid_projects)}] 检测项目: {name}")
            print(f"{'='*60}")

        await run_diagnostic_for_project(project_name, args, config_manager)


async def main():
    """主函数"""
    args = parse_arguments()

    # 显示版本信息
    if args.version:
        show_version()

    # 设置日志
    setup_logging(args.verbose)

    # 创建配置文件
    if args.create_config:
        create_default_configs(args.config_dir)
        return

    # 初始化配置管理器
    config_manager = ConfigManager(args.config_dir)

    # 列出项目
    if args.list_projects:
        list_projects(config_manager)
        return

    # 项目检测逻辑
    if args.project:
        # 检测指定项目
        await run_diagnostic_for_project(args.project, args, config_manager)
    else:
        # 交互式选择项目
        await interactive_project_selection(args, config_manager)


if __name__ == "__main__":
    try:
        # 在 Windows 上使用 WindowsSelectorEventLoopPolicy 避免 ProactorEventLoop 的资源清理警告
        # 参考: https://github.com/aio-libs/aiohttp/issues/4324
        if sys.platform == "win32":
            # 设置事件循环策略以避免 ProactorEventLoop 在 aiohttp 场景下的资源清理警告
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # 仅抑制已知的 aiohttp 相关资源警告（Windows + ProactorEventLoop 的已知问题）
            # TODO: 在 aiohttp 修复此问题后移除此变通方案
            import warnings

            warnings.filterwarnings(
                "ignore",
                category=ResourceWarning,
                message="unclosed transport",
                module="asyncio"
            )

        asyncio.run(main())
        # 运行完成后暂停，让用户有机会复制日志
        print("\n" + "=" * 60)
        print("💡 提示：可以向上滚动查看完整日志")
        print("=" * 60)
        input("\n按 Enter 键退出...")
    except KeyboardInterrupt:
        print("\n[*] 用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 程序执行出错: {e}")
        # 检查是否有详细模式参数
        if len(sys.argv) > 1 and ("-v" in sys.argv or "--verbose" in sys.argv):
            import traceback

            traceback.print_exc()
        input("\n按 Enter 键退出...")
        sys.exit(1)
