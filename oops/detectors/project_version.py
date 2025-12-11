"""
项目版本检测器
检测项目本地版本和远程最新版本
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from oops.core.config import DetectionRule

logger = logging.getLogger(__name__)


class ProjectVersionDetector(DetectionRule):
    """项目版本检测器 - 检测项目版本状态"""

    def __init__(self):
        super().__init__(
            name="project_version",
            description="项目版本状态检测",
            severity="warning",
        )
        self.timeout = 10

    async def check_async(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行项目版本检测（异步版本）"""
        try:
            # 检查配置和项目路径
            check_result = self._check_config(config)
            if check_result:
                return check_result

            project_path = config.get("project", {}).get("paths", {}).get("install_path", "")
            version_config = config.get("checks", {}).get("project_version", {})

            # 收集版本信息
            local_version = self._get_local_version(project_path)
            launcher_version = self._get_launcher_version(project_path)
            remote_version = await self._get_remote_version(version_config)

            # 分析版本信息并生成结果
            return self._analyze_version_info(local_version, launcher_version, remote_version)

        except Exception as e:
            logger.error(f"项目版本检测失败: {e}")
            return {"status": "error", "message": f"项目版本检测失败: {str(e)}"}

    def _check_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检查配置和项目路径"""
        version_config = config.get("checks", {}).get("project_version", {})
        if not version_config.get("enabled", False):
            return {"status": "skipped", "message": "项目版本检测未启用"}

        project_path = config.get("project", {}).get("paths", {}).get("install_path", "")
        if not project_path:
            return {"status": "skipped", "message": "未配置项目路径"}
        return None

    async def _get_remote_version(self, version_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取远程版本信息"""
        remote_version = None
        gitee_repo = version_config.get("gitee_repo", "")
        github_repo = version_config.get("github_repo", "")

        if gitee_repo:
            parts = gitee_repo.split("/")
            if len(parts) == 2:
                remote_version = await self._get_remote_version_gitee(parts[0], parts[1])

        if not remote_version and github_repo:
            parts = github_repo.split("/")
            if len(parts) == 2:
                remote_version = await self._get_remote_version_github(parts[0], parts[1])

        return remote_version

    def _analyze_version_info(self, local_version: Dict[str, Any], launcher_version: Dict[str, Any], remote_version: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析版本信息并生成检测结果"""
        issues = []
        warnings = []
        recommendations = []

        if not local_version.get("is_git_repo"):
            return self._generate_non_git_result(local_version, launcher_version, issues, warnings, recommendations)

        # 如果本地版本信息不完整
        if not local_version.get("current_tag") and not local_version.get("current_commit"):
            warnings.append("无法获取本地版本信息")

        # 检查启动器版本
        self._check_launcher_version(launcher_version, warnings)

        # 比较版本并生成警告和建议
        if remote_version:
            self._compare_versions(local_version, launcher_version, remote_version, warnings, recommendations)

        version_info = {
            "local": local_version,
            "remote": remote_version,
        }

        status = "success" if not issues else "warning"
        message = "项目版本检测完成"
        if not remote_version:
            message += "（无法获取远程版本，请检查网络连接）"

        return {
            "status": status,
            "message": message,
            "details": {
                "version": version_info,
                "launcher": launcher_version,
                "issues": issues,
                "warnings": warnings,
                "recommendations": recommendations,
            },
        }

    def _generate_non_git_result(self, local_version: Dict[str, Any], launcher_version: Dict[str, Any], issues: List[str], warnings: List[str], recommendations: List[str]) -> Dict[str, Any]:
        """生成非Git仓库的检测结果"""
        return {
            "status": "info",
            "message": "项目不是 Git 仓库，跳过版本检测",
            "details": {
                "version": {"local": local_version, "remote": None},
                "launcher": launcher_version,
                "issues": issues,
                "warnings": warnings,
                "recommendations": recommendations,
            },
        }

    def _check_launcher_version(self, launcher_version: Dict[str, Any], warnings: List[str]) -> None:
        """检查启动器版本并生成警告"""
        launcher_ver = launcher_version.get("version", "")
        if not launcher_version.get("exists"):
            warnings.append("未找到启动器文件 (OneDragon-Launcher.exe)")
        elif not launcher_ver:
            error_msg = launcher_version.get("error", "未知错误")
            warnings.append(f"无法获取启动器版本: {error_msg}")

    def _compare_versions(self, local_version: Dict[str, Any], launcher_version: Dict[str, Any], remote_version: Dict[str, Any], warnings: List[str], recommendations: List[str]) -> None:
        """比较版本并生成警告和建议"""
        remote_tag = remote_version.get("tag_name", "")
        launcher_ver = launcher_version.get("version", "")

        # 优先使用启动器版本进行比对
        if launcher_ver:
            if launcher_ver != remote_tag:
                warnings.append(f"启动器版本 ({launcher_ver}) 与远程最新版本 ({remote_tag}) 不一致")
                recommendations.append(f"建议更新到最新版本 {remote_tag}")
        else:
            # 如果没有启动器版本，使用 Git tag 进行比对
            local_tag = local_version.get("current_tag", "")
            if local_tag:
                if local_tag != remote_tag:
                    warnings.append(f"本地 Git 标签 ({local_tag}) 与远程最新版本 ({remote_tag}) 不一致")
                    recommendations.append(f"建议更新到最新版本 {remote_tag}")
            else:
                # 既没有启动器版本，也没有 Git tag
                warnings.append("无法确定本地版本（未找到启动器或 Git 标签）")
                recommendations.append(f"远程最新版本: {remote_tag}，建议检查是否需要更新")

    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行项目版本检测（同步版本，用于兼容）"""
        import asyncio

        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建一个任务
                return asyncio.create_task(self.check_async(config))
            else:
                # 如果循环未运行，直接运行
                return loop.run_until_complete(self.check_async(config))
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            return asyncio.run(self.check_async(config))

    def _get_local_version(self, project_path: str) -> Dict[str, Any]:
        """获取本地项目版本信息"""
        try:
            git_dir = Path(project_path) / ".git"
            if not git_dir.exists():
                return {"is_git_repo": False}

            version_info = {"is_git_repo": True}

            # 获取当前分支
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version_info["current_branch"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"获取当前分支失败: {e}")

            # 获取当前 commit
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version_info["current_commit"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"获取当前 commit 失败: {e}")

            # 获取当前 tag（如果有）
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--exact-match"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version_info["current_tag"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"获取当前 tag 失败: {e}")

            # 获取最后更新时间
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ci"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version_info["last_update"] = result.stdout.strip()
            except Exception as e:
                logger.debug(f"获取最后更新时间失败: {e}")

            # 检查是否有未提交的更改
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    has_changes = bool(result.stdout.strip())
                    version_info["has_uncommitted_changes"] = has_changes
            except Exception as e:
                logger.debug(f"检查未提交更改失败: {e}")

            return version_info
        except Exception as e:
            logger.error(f"获取本地版本失败: {e}")
            return {"is_git_repo": False, "error": str(e)}

    def _get_launcher_version(self, project_path: str) -> Dict[str, Any]:
        """获取启动器版本信息"""
        try:
            launcher_path = Path(project_path) / "OneDragon-Launcher.exe"
            if not launcher_path.exists():
                return {"exists": False, "version": None, "path": str(launcher_path)}

            # 通过 --version 参数获取版本号
            try:
                result = subprocess.run(
                    [str(launcher_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    version_output = result.stdout.strip()
                    # 解析版本号（格式可能是 "OneDragon Launcher v2.3.3" 或 "v2.3.3"）
                    parts = version_output.split("v", 1)
                    version = f"v{parts[1]}" if len(parts) > 1 else version_output
                    return {
                        "exists": True,
                        "version": version,
                        "path": str(launcher_path),
                    }
                else:
                    return {
                        "exists": True,
                        "version": None,
                        "error": f"启动器返回错误代码: {result.returncode}",
                        "path": str(launcher_path),
                    }
            except subprocess.TimeoutExpired:
                return {
                    "exists": True,
                    "version": None,
                    "error": "获取版本超时",
                    "path": str(launcher_path),
                }
            except Exception as e:
                return {
                    "exists": True,
                    "version": None,
                    "error": f"执行失败: {str(e)}",
                    "path": str(launcher_path),
                }
        except Exception as e:
            logger.debug(f"获取启动器版本失败: {e}")
            return {"exists": False, "error": str(e)}

    async def _get_remote_version_gitee(
        self, owner: str, repo: str
    ) -> Optional[Dict[str, Any]]:
        """从 Gitee API 获取最新版本"""
        try:
            api_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/releases/latest"
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "tag_name": data.get("tag_name"),
                            "name": data.get("name"),
                            "published_at": data.get("created_at"),
                            "source": "gitee",
                        }
        except Exception as e:
            logger.debug(f"从 Gitee 获取版本失败: {e}")
        return None

    async def _get_remote_version_github(
        self, owner: str, repo: str
    ) -> Optional[Dict[str, Any]]:
        """从 GitHub API 获取最新版本"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "tag_name": data.get("tag_name"),
                            "name": data.get("name"),
                            "published_at": data.get("published_at"),
                            "source": "github",
                        }
        except Exception as e:
            logger.debug(f"从 GitHub 获取版本失败: {e}")
        return None

    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        details = result.get("details", {})
        recommendations = details.get("recommendations", [])
        return "; ".join(recommendations) if recommendations else ""
