"""
Python 环境检测器
检测 Python 版本、包管理器类型、虚拟环境及依赖完整性
"""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class PythonEnvironmentDetector(DetectionRule):
    """Python 环境检测器"""

    def __init__(self):
        super().__init__(
            name="python_environment",
            description="Python 环境检测",
            severity="warning",
        )

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Python 环境检测"""
        try:
            env_config = config.get("checks", {}).get("environment", {})
            project_path = env_config.get("project_path", "")

            # 收集环境信息
            environment_info = {
                "python_version": self._get_python_version(),
                "package_manager": self._detect_package_manager(project_path),
                "virtual_env": self._check_virtual_environment(
                    project_path, env_config
                ),
            }

            # 如果检测到虚拟环境，检查依赖完整性
            if environment_info["virtual_env"].get("venv_exists"):
                venv_path = environment_info["virtual_env"].get("venv_path")

                # 查找依赖文件（支持多种格式）
                dependency_file = None
                dependency_type = None

                # 优先查找 requirements.txt
                requirements_txt = os.path.join(project_path, "requirements.txt")
                if os.path.exists(requirements_txt):
                    dependency_file = requirements_txt
                    dependency_type = "requirements.txt"
                # 其次查找 pyproject.toml
                elif os.path.exists(os.path.join(project_path, "pyproject.toml")):
                    dependency_file = os.path.join(project_path, "pyproject.toml")
                    dependency_type = "pyproject.toml"
                # 最后查找 uv.lock
                elif os.path.exists(os.path.join(project_path, "uv.lock")):
                    dependency_file = os.path.join(project_path, "uv.lock")
                    dependency_type = "uv.lock"

                if dependency_file:
                    environment_info["dependencies"] = self._check_dependencies(
                        venv_path, dependency_file, dependency_type
                    )

            # 分析问题
            issues = []
            warnings = []
            recommendations = []

            # Python 版本检查
            python_check = environment_info["python_version"]
            if not python_check.get("compatible", True):
                issues.append(
                    f"Python 版本不兼容: {python_check.get('current')} (需要 {python_check.get('required')})"
                )
                recommendations.append(
                    f"请安装 Python {python_check.get('required')} 或更高版本"
                )

            # 虚拟环境检查
            venv_check = environment_info["virtual_env"]
            if not venv_check.get("venv_exists") and env_config.get("virtual_env"):
                warnings.append("未检测到虚拟环境")
                recommendations.append("建议创建Python虚拟环境以隔离项目依赖")

            # 依赖检查
            if "dependencies" in environment_info:
                deps = environment_info["dependencies"]
                if not deps.get("complete"):
                    missing = deps.get("missing", [])
                    if missing:
                        issues.append(f"缺失 {len(missing)} 个依赖包")
                        recommendations.append(
                            f"运行 pip install -r requirements.txt 安装缺失的包"
                        )

                    version_mismatch = deps.get("version_mismatch", [])
                    if version_mismatch:
                        warnings.append(f"{len(version_mismatch)} 个包版本不匹配")
                        recommendations.append("检查并更新不匹配的包版本")

            # 确定状态
            if issues:
                status = "error"
                message = f"Python 环境存在 {len(issues)} 个问题"
            elif warnings:
                status = "warning"
                message = f"Python 环境存在 {len(warnings)} 个警告"
            else:
                status = "success"
                message = "Python 环境检查通过"

            return {
                "status": status,
                "message": message,
                "details": {
                    "environment": environment_info,
                    "issues": issues,
                    "warnings": warnings,
                    "recommendations": recommendations,
                },
            }
        except Exception as e:
            logger.error(f"Python 环境检测失败: {e}")
            return {"status": "error", "message": f"Python 环境检测失败: {str(e)}"}

    def _get_python_version(self) -> Dict[str, Any]:
        """获取 Python 版本信息"""
        current_version = sys.version_info
        return {
            "current": f"{current_version.major}.{current_version.minor}.{current_version.micro}",
            "major": current_version.major,
            "minor": current_version.minor,
            "micro": current_version.micro,
        }

    def _detect_package_manager(self, project_path: str) -> Dict[str, Any]:
        """检测包管理器类型"""
        manager_type = "unknown"
        manager_version = None
        manager_path = None

        try:
            # 检查是否在 conda 环境
            if os.environ.get("CONDA_DEFAULT_ENV"):
                manager_type = "conda"
                try:
                    result = subprocess.run(
                        ["conda", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        manager_version = result.stdout.strip()
                except:
                    pass

            # 检查项目特定文件和工具
            elif project_path:
                # 检查 OneDragon 项目的嵌入式 UV
                uv_embedded = os.path.join(project_path, ".install", "uv", "uv.exe")
                if os.path.exists(uv_embedded):
                    manager_type = "uv"
                    manager_path = uv_embedded
                    try:
                        result = subprocess.run(
                            [uv_embedded, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            manager_version = result.stdout.strip()
                    except:
                        pass
                # 检查 uv.lock 文件
                elif os.path.exists(os.path.join(project_path, "uv.lock")):
                    manager_type = "uv"
                    # 尝试系统 UV
                    try:
                        result = subprocess.run(
                            ["uv", "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            manager_version = result.stdout.strip()
                    except:
                        pass
                elif os.path.exists(os.path.join(project_path, "poetry.lock")):
                    manager_type = "poetry"
                elif os.path.exists(os.path.join(project_path, "Pipfile")):
                    manager_type = "pipenv"

            # 默认检查 pip
            if manager_type == "unknown":
                try:
                    result = subprocess.run(
                        ["pip", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        manager_type = "pip"
                        manager_version = result.stdout.strip()
                except:
                    pass

        except Exception as e:
            logger.debug(f"检测包管理器失败: {e}")

        return {
            "type": manager_type,
            "version": manager_version,
            "path": manager_path,
        }

    def _check_virtual_environment(
        self, project_path: str, env_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检测虚拟环境"""
        # 检查是否在虚拟环境中运行
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

        venv_exists = False
        venv_path = None

        if project_path:
            # 检查常见的虚拟环境目录
            common_venv_names = [".venv", "venv", "env", ".env"]

            # 首先在项目路径中查找
            for venv_name in common_venv_names:
                potential_venv = Path(project_path) / venv_name
                if potential_venv.exists() and potential_venv.is_dir():
                    if self._is_valid_venv(potential_venv):
                        venv_exists = True
                        venv_path = str(potential_venv)
                        break

            # 如果没找到，向上查找父目录（最多3层）
            if not venv_exists:
                current_path = Path(project_path)
                for _ in range(3):
                    try:
                        parent = current_path.parent
                        if parent == current_path:  # 已到根目录
                            break

                        for venv_name in common_venv_names:
                            potential_venv = parent / venv_name
                            if potential_venv.exists() and potential_venv.is_dir():
                                if self._is_valid_venv(potential_venv):
                                    venv_exists = True
                                    venv_path = str(potential_venv)
                                    logger.info(f"在父目录找到虚拟环境: {venv_path}")
                                    break

                        if venv_exists:
                            break

                        current_path = parent
                    except (PermissionError, OSError):
                        break

            # 如果还没找到，扫描项目根目录中的所有目录
            if not venv_exists:
                try:
                    for item in Path(project_path).iterdir():
                        if item.is_dir() and self._is_valid_venv(item):
                            venv_exists = True
                            venv_path = str(item)
                            break
                except (PermissionError, OSError):
                    pass

        return {
            "in_venv": in_venv,
            "venv_exists": venv_exists,
            "venv_path": venv_path,
        }

    def _is_valid_venv(self, venv_path: Path) -> bool:
        """验证是否是有效的虚拟环境"""
        try:
            import platform

            system = platform.system().lower()

            if system == "windows":
                activate_bat = venv_path / "Scripts" / "activate.bat"
                activate_ps1 = venv_path / "Scripts" / "Activate.ps1"
                python_exe = venv_path / "Scripts" / "python.exe"
                return (
                    activate_bat.exists() or activate_ps1.exists()
                ) and python_exe.exists()
            else:
                activate_sh = venv_path / "bin" / "activate"
                python_bin = venv_path / "bin" / "python"
                return activate_sh.exists() and python_bin.exists()
        except Exception as e:
            logger.debug(f"验证虚拟环境失败: {e}")
            return False

    def _check_dependencies(
        self,
        venv_path: str,
        dependency_file: str,
        dependency_type: str = "requirements.txt",
    ) -> Dict[str, Any]:
        """检查虚拟环境中的依赖完整性"""
        try:
            # 获取已安装的包
            installed_packages = self._get_installed_packages(venv_path)

            # 对于 pyproject.toml 和 uv.lock，只返回基本信息
            if dependency_type in ["pyproject.toml", "uv.lock"]:
                return {
                    "complete": True,  # 假设完整（无法精确检查）
                    "dependency_file": dependency_type,
                    "total_installed": len(installed_packages),
                    "message": f"检测到 {dependency_type}，已安装 {len(installed_packages)} 个包",
                }

            # 解析 requirements.txt
            required_packages = self._parse_requirements(dependency_file)

            # 比对
            missing = []
            version_mismatch = []

            for pkg_name, required_version in required_packages.items():
                if pkg_name not in installed_packages:
                    missing.append(pkg_name)
                elif required_version and not self._version_matches(
                    installed_packages[pkg_name], required_version
                ):
                    version_mismatch.append(
                        {
                            "package": pkg_name,
                            "required": required_version,
                            "installed": installed_packages[pkg_name],
                        }
                    )

            return {
                "complete": len(missing) == 0 and len(version_mismatch) == 0,
                "missing": missing,
                "version_mismatch": version_mismatch,
                "total_required": len(required_packages),
                "total_installed": len(installed_packages),
                "dependency_file": dependency_type,
            }
        except Exception as e:
            logger.error(f"检查依赖失败: {e}")
            return {"complete": False, "error": str(e)}

    def _parse_requirements(self, requirements_file: str) -> Dict[str, Optional[str]]:
        """解析 requirements.txt"""
        packages = {}
        try:
            with open(requirements_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # 简单解析，支持 package==version 格式
                        if "==" in line:
                            pkg_name, version = line.split("==", 1)
                            packages[pkg_name.strip()] = version.strip()
                        elif ">=" in line:
                            pkg_name = line.split(">=", 1)[0].strip()
                            packages[pkg_name] = None  # 不检查具体版本
                        else:
                            packages[line] = None
        except Exception as e:
            logger.error(f"解析 requirements.txt 失败: {e}")
        return packages

    def _get_installed_packages(self, venv_path: str) -> Dict[str, str]:
        """获取虚拟环境中已安装的包"""
        packages = {}
        try:
            import platform

            system = platform.system().lower()

            # 尝试使用 pip
            pip_exe = (
                os.path.join(venv_path, "Scripts", "pip.exe")
                if system == "windows"
                else os.path.join(venv_path, "bin", "pip")
            )

            if os.path.exists(pip_exe):
                result = subprocess.run(
                    [pip_exe, "list", "--format=freeze"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if "==" in line:
                            pkg_name, version = line.split("==", 1)
                            packages[pkg_name.strip()] = version.strip()
                    logger.debug(f"从虚拟环境获取到 {len(packages)} 个包（使用 pip）")
                    return packages
                else:
                    logger.debug(f"pip list 执行失败: {result.stderr}")
            else:
                logger.debug(f"pip 不存在于虚拟环境: {pip_exe}")

            # 如果 pip 不可用，尝试使用 Python 的 importlib.metadata
            python_exe = (
                os.path.join(venv_path, "Scripts", "python.exe")
                if system == "windows"
                else os.path.join(venv_path, "bin", "python")
            )

            if os.path.exists(python_exe):
                # 使用 importlib.metadata 列出包
                py_code = """
import importlib.metadata
for dist in importlib.metadata.distributions():
    print(f"{dist.name}=={dist.version}")
"""
                result = subprocess.run(
                    [python_exe, "-c", py_code],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split("\n"):
                        if "==" in line:
                            pkg_name, version = line.split("==", 1)
                            packages[pkg_name.strip()] = version.strip()
                    logger.debug(
                        f"从虚拟环境获取到 {len(packages)} 个包（使用 importlib.metadata）"
                    )
                else:
                    logger.debug(f"importlib.metadata 执行失败: {result.stderr}")
        except Exception as e:
            logger.error(f"获取已安装包列表失败: {e}")
        return packages

    def _version_matches(self, installed_version: str, required_version: str) -> bool:
        """检查版本是否匹配"""
        # 简单的版本比较，可以扩展为更复杂的版本匹配逻辑
        return installed_version == required_version

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        details = result.get("details", {})
        recommendations = details.get("recommendations", [])
        return "; ".join(recommendations) if recommendations else ""
