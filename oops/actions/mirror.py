"""
oops mirror —— 切换目标项目(绝区零一条龙)的 origin 远程

把 origin 指向 CNB(或 GitHub/Gitee)镜像,修复启动器自更新
(GitHub 慢/不通、blobless 部分克隆每次回源)的问题。

只动 origin 与备份远程,不碰个人 fork 远程(myself_main / kawayiYokami 等)。
"""

import argparse
import logging

from oops.actions import git_ops

logger = logging.getLogger(__name__)

# 默认镜像源 URL(可通过 --url / --to 覆盖)
MIRROR_URLS = {
    "cnb": "https://cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon.git",
    "github": "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git",
    "gitee": "https://gitee.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git",
}
# 旧 origin(GitHub)会被改名为此,作为可回退备份
GITHUB_FALLBACK_REMOTE = "github"


def _select_target_url(args: argparse.Namespace):
    """返回 (url, 可读标签)。无法确定返回 (None, None)。"""
    if getattr(args, "url", None):
        return args.url, args.url
    to = getattr(args, "to", "cnb")
    url = MIRROR_URLS.get(to)
    if not url:
        return None, None
    return url, f"{to}  ({url})"


def cmd_mirror(args: argparse.Namespace) -> int:
    path = git_ops.resolve_target_path(getattr(args, "path", None))
    if not path:
        print("[ERROR] 未找到目标项目。请在项目目录中运行,或用 --path 指定。")
        return 2
    print(f"[*] 目标项目: {path}")

    if not git_ops.is_git_repo(path):
        print("[ERROR] 该目录不是 git 仓库。")
        return 2

    before = git_ops.list_remotes(path)
    print("[*] 当前远程:")
    for name, urls in before.items():
        print(f"    {name}\t{urls.get('fetch', '')}")

    target_url, target_label = _select_target_url(args)
    if not target_url:
        print(f"[ERROR] 未知镜像源。可选: {', '.join(MIRROR_URLS)},或用 --url 指定。")
        return 2
    print(f"[*] 目标 origin: {target_label}")

    old_origin = git_ops.get_remote_url(path, "origin")
    changed = False
    if old_origin and old_origin != target_url:
        changed = True
        if not git_ops.remote_exists(path, GITHUB_FALLBACK_REMOTE):
            print(f"[*] 保留旧 origin 为备份远程 '{GITHUB_FALLBACK_REMOTE}'")
            git_ops.rename_remote(path, "origin", GITHUB_FALLBACK_REMOTE)
            git_ops.set_remote_url(path, "origin", target_url, add=True)
        else:
            print(f"[*] 备份远程 '{GITHUB_FALLBACK_REMOTE}' 已存在,直接更新 origin")
            git_ops.set_remote_url(path, "origin", target_url)
    elif old_origin:
        print("[*] origin 已指向目标,无需修改")
    else:
        changed = True
        git_ops.set_remote_url(path, "origin", target_url, add=True)

    after = git_ops.list_remotes(path)
    print("[*] 修改后远程:")
    for name, urls in after.items():
        print(f"    {name}\t{urls.get('fetch', '')}")

    if not getattr(args, "no_verify", False):
        print("[*] 验证可达性: git fetch origin --prune ...")
        r = git_ops.run_git(
            ["fetch", "origin", "--prune"], cwd=path, timeout=git_ops.FETCH_TIMEOUT
        )
        if r.returncode == 0:
            print("[+] fetch 成功,origin 可达。")
        else:
            print(f"[!] fetch 失败(返回码 {r.returncode}):")
            print(r.stderr.strip() or r.stdout.strip())
            print("[!] 镜像可能尚未建立或不可达。可用 --no-verify 跳过此检查。")
            return 1
    else:
        print("[*] 已跳过可达性验证(--no-verify)。")

    print()
    if changed:
        print("[完成] origin 已切换。OneDragon 启动器自更新现在会从此镜像拉取。")
        print("[提示] 随后可运行: oops sync   # 对齐到 HEAD")
    else:
        print("[完成] origin 已是指定目标,无需切换。")
    return 0
