"""
oops sync —— 把目标项目代码对齐到远程 HEAD

策略:硬重置 + 自动备份
  - 打备份分支 oops-backup-<时间戳>(保存当前 HEAD)
  - 若工作区有改动,再 git stash push -u(保存未提交改动)
  - 然后 git fetch + git reset --hard <remote>/HEAD + git clean -fd
所有备份均可通过提示的命令恢复。

注意:若目标是部分克隆(blobless)且 origin 已切到完整 CNB 镜像,
reset --hard 会从新 origin 按需拉取 blob(国内快),链路自愈。
"""

import argparse
import logging
import time
from typing import Optional

from oops.actions import git_ops

logger = logging.getLogger(__name__)


def backup_tag() -> str:
    """生成备份名(也用作测试纯函数)。"""
    return time.strftime("oops-backup-%Y%m%d-%H%M%S")


def resolve_align_target(
    path: str, remote: str, branch: Optional[str]
) -> Optional[str]:
    """返回对齐目标引用,如 'origin/main'。"""
    if branch:
        return f"{remote}/{branch}"
    head_branch = git_ops.resolve_remote_head(path, remote)
    if head_branch:
        return f"{remote}/{head_branch}"
    cur = git_ops.current_branch(path)
    if cur:
        return f"{remote}/{cur}"
    return None


def version_tuple(v: str):
    """纯函数:把 'v1.2.3' 解析为 (1,2,3),便于测试。"""
    parts = []
    for p in (v or "").lstrip("v").split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def cmd_sync(args: argparse.Namespace) -> int:
    if not git_ops.ensure_git_or_report():
        return 3
    path = git_ops.resolve_target_path(getattr(args, "path", None))
    if not path:
        print("[ERROR] 未找到目标项目。请在项目目录中运行,或用 --path 指定。")
        return 2
    print(f"[*] 目标项目: {path}")

    if not git_ops.is_git_repo(path):
        print("[ERROR] 该目录不是 git 仓库。")
        return 2

    remote = getattr(args, "remote", None) or "origin"
    branch = getattr(args, "branch", None)
    no_backup = getattr(args, "no_backup", False)
    no_clean = getattr(args, "no_clean", False)

    before_sha = git_ops.get_short_sha(path)
    print(f"[*] 当前: {git_ops.current_branch(path)} @ {before_sha}")

    print(f"[*] git fetch {remote} ...")
    fr = git_ops.run_git(
        ["fetch", remote, "--prune", "--tags"],
        cwd=path,
        timeout=git_ops.FETCH_TIMEOUT,
    )
    if fr.returncode != 0:
        print(f"[ERROR] fetch 失败(返回码 {fr.returncode}):")
        print(fr.stderr.strip() or fr.stdout.strip())
        return 1

    target = resolve_align_target(path, remote, branch)
    if not target:
        print(
            f"[ERROR] 无法确定对齐目标(远程 {remote} 的 HEAD/分支均无法解析)。"
            f"可用 --branch 指定。"
        )
        return 2
    print(f"[*] 对齐目标: {target}")

    if not git_ops.verify_ref(path, target):
        print(f"[ERROR] 远程引用不存在: {target}")
        return 1

    # ===== 备份 =====
    backup_branch = None
    stash_label = None
    if not no_backup:
        backup_branch = backup_tag()
        br = git_ops.run_git(["branch", backup_branch], cwd=path, timeout=15)
        if br.returncode == 0:
            print(f"[备份] 已创建备份分支: {backup_branch}(保存当前 HEAD)")
        else:
            print(f"[备份] 创建备份分支失败: {br.stderr.strip()}")
            backup_branch = None

        if git_ops.is_dirty(path):
            stash_label = backup_tag()
            sr = git_ops.run_git(
                ["stash", "push", "-u", "-m", stash_label], cwd=path, timeout=60
            )
            out = sr.stdout + sr.stderr
            if sr.returncode == 0 and "No local changes" not in out:
                print(f"[备份] 未提交改动已 stash: {stash_label}")
            else:
                print(f"[备份] stash 未提交改动失败或无改动: {out.strip()}")
                stash_label = None
        else:
            print("[*] 工作区干净,无需 stash。")

    # ===== 硬重置 =====
    rr = git_ops.run_git(["reset", "--hard", target], cwd=path, timeout=300)
    if rr.returncode != 0:
        print("[ERROR] reset 失败:")
        print(rr.stderr.strip() or rr.stdout.strip())
        return 1
    print(f"[+] 已 reset --hard 到 {target}")

    if not no_clean:
        cr = git_ops.run_git(["clean", "-fd"], cwd=path, timeout=60)
        if cr.returncode == 0:
            print("[+] 已清理未跟踪文件 (git clean -fd)")
        else:
            print(f"[!] clean 失败(可忽略): {cr.stderr.strip()}")

    # 重设上游跟踪到新 origin/<branch>,让 git status 与启动器更新走新 origin
    cur_branch = git_ops.current_branch(path)
    if cur_branch and cur_branch != "HEAD":
        head_branch = branch or git_ops.resolve_remote_head(path, remote) or cur_branch
        git_ops.run_git(
            ["branch", f"--set-upstream-to={remote}/{head_branch}", cur_branch],
            cwd=path,
            timeout=15,
        )

    after_sha = git_ops.get_short_sha(path)
    print()
    print(f"[完成] 已对齐到 HEAD。 {before_sha} -> {after_sha}")
    if backup_branch:
        print(f"[恢复] 如需回滚提交: git reset --hard {backup_branch}")
    if stash_label:
        print(f"[恢复] 如需恢复未提交改动: git stash pop  (stash 标记: {stash_label})")
    if no_backup:
        print("[!] 已用 --no-backup,本地改动已被丢弃且无法恢复。")
    return 0
