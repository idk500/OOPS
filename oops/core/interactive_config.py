"""
交互式配置工具
帮助用户首次配置项目路径
"""

import logging
from pathlib import Path
from typing import Optional

import yaml

from oops.core.path_resolver import PathResolver

logger = logging.getLogger(__name__)


class InteractiveConfig:
    """交互式配置助手"""

    @staticmethod
    def prompt_install_path(project_name: str) -> Optional[str]:
        """
        提示用户输入项目安装路径

        Args:
            project_name: 项目名称

        Returns:
            用户输入的路径，如果取消则返回 None
        """
        print("\n" + "=" * 60)
        print(f"📁 首次运行 - 需要配置项目路径")
        print("=" * 60)
        print(f"\n项目: {project_name}")
        print("\n请输入项目的安装路径，支持以下格式：")
        print("  1. 绝对路径: E:/ZZZ-1D 或 C:/Games/ZenlessZoneZero-OneDragon")
        print("  2. 相对路径: ../ZenlessZoneZero-OneDragon")
        print("  3. 环境变量: ${ZZZ_INSTALL_PATH}")
        print("  4. 输入 'auto' 尝试自动检测")
        print("  5. 输入 'skip' 跳过配置（部分功能可能不可用）")
        print()

        while True:
            try:
                user_input = input("请输入路径 > ").strip()

                if not user_input:
                    print("❌ 路径不能为空，请重新输入")
                    continue

                if user_input.lower() == "skip":
                    print("⚠️  跳过路径配置，部分功能可能不可用")
                    return None

                # 尝试解析路径
                resolved_path = PathResolver.resolve_path(
                    user_input, base_dir=str(Path.cwd()), project_name=project_name
                )

                if resolved_path:
                    # 验证路径
                    path = Path(resolved_path)
                    if path.exists():
                        print(f"✅ 路径有效: {resolved_path}")

                        # 确认
                        confirm = input("确认使用此路径？(y/n) > ").strip().lower()
                        if confirm in ["y", "yes", ""]:
                            return resolved_path
                        else:
                            print("已取消，请重新输入")
                            continue
                    else:
                        print(f"⚠️  路径不存在: {resolved_path}")
                        use_anyway = (
                            input("是否仍然使用此路径？(y/n) > ").strip().lower()
                        )
                        if use_anyway in ["y", "yes"]:
                            return resolved_path
                        else:
                            continue
                else:
                    print("❌ 无法解析路径，请检查输入格式")
                    continue

            except KeyboardInterrupt:
                print("\n\n⚠️  配置已取消")
                return None
            except Exception as e:
                print(f"❌ 错误: {e}")
                continue

    @staticmethod
    def save_install_path(
        project_name: str, install_path: str, config_dir: str = "configs"
    ) -> bool:
        """
        保存安装路径到配置文件

        Args:
            project_name: 项目名称
            install_path: 安装路径
            config_dir: 配置目录

        Returns:
            是否保存成功
        """
        try:
            config_file = Path(config_dir) / f"{project_name}.yaml"
            if not config_file.exists():
                logger.error(f"配置文件不存在: {config_file}")
                return False

            # 读取现有配置
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 更新路径
            if "project" not in config:
                config["project"] = {}
            if "paths" not in config["project"]:
                config["project"]["paths"] = {}

            config["project"]["paths"]["install_path"] = install_path

            # 保存配置
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

            print(f"✅ 配置已保存到: {config_file}")
            return True

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            print(f"❌ 保存配置失败: {e}")
            return False

    @staticmethod
    def check_and_prompt_if_needed(
        project_name: str, config: dict, config_dir: str = "configs"
    ) -> bool:
        """
        检查配置，如果需要则提示用户配置

        Args:
            project_name: 项目名称
            config: 项目配置
            config_dir: 配置目录

        Returns:
            是否配置成功
        """
        install_path = (
            config.get("project", {}).get("paths", {}).get("install_path", "")
        )

        # 如果路径为空或无效，提示用户配置
        if not install_path or not Path(install_path).exists():
            print(f"\n⚠️  项目路径未配置或无效: {install_path or '(空)'}")

            # 提示用户输入
            new_path = InteractiveConfig.prompt_install_path(project_name)

            if new_path:
                # 保存配置
                if InteractiveConfig.save_install_path(
                    project_name, new_path, config_dir
                ):
                    # 更新当前配置
                    config["project"]["paths"]["install_path"] = new_path
                    return True
                else:
                    return False
            else:
                return False

        return True
