"""
oops/actions 子命令的测试

- 纯函数:版本比较、备份名、tag 规范化
- 集成:在临时 git 仓 + 本地 bare 远程上验证 mirror / sync 的真实行为
"""

import re
import subprocess
import tempfile
from argparse import Namespace
from pathlib import Path

import pytest

# ===== git 临时仓辅助 =====


def _git(*args, cwd=None):
    r = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"git {args} 失败: {r.stderr}"
    return r


def _cfg_identity(path):
    _git("config", "user.email", "test@test", cwd=str(path))
    _git("config", "user.name", "test", cwd=str(path))


def _make_repo(path, msgs):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "main", str(path))
    _cfg_identity(path)
    shas = []
    for m in msgs:
        _git("commit", "--allow-empty", "-m", m, cwd=str(path))
        shas.append(_git("rev-parse", "--short", "HEAD", cwd=str(path)).stdout.strip())
    return path, shas


def _make_bare(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "--bare", "-b", "main", str(path))
    return path


# ===== 纯函数 =====


def test_version_tuple():
    from oops.actions.self_update import version_tuple

    assert version_tuple("v1.2.3") == (1, 2, 3)
    assert version_tuple("0.3.0") == (0, 3, 0)
    assert version_tuple("v2") == (2,)


def test_is_newer():
    from oops.actions.self_update import is_newer

    assert is_newer("v0.3.0", "0.2.3") is True
    assert is_newer("0.2.3", "0.3.0") is False
    assert is_newer("v0.3.0", "0.3.0") is False


def test_normalize_tag():
    from oops.actions.self_update import normalize_tag

    assert normalize_tag("v0.3.0") == "0.3.0"
    assert normalize_tag("1.2") == "1.2"
    assert normalize_tag("") == ""


def test_backup_tag_format():
    from oops.actions.sync import backup_tag

    assert re.match(r"^oops-backup-\d{8}-\d{6}$", backup_tag())


# ===== git_ops 基础 =====


def test_is_git_repo_and_list_remotes(tmp_path):
    from oops.actions import git_ops

    repo = tmp_path / "repo"
    _make_repo(repo, ["init"])
    assert git_ops.is_git_repo(str(repo)) is True

    notrepo = tmp_path / "empty"
    notrepo.mkdir()
    assert git_ops.is_git_repo(str(notrepo)) is False

    bare = _make_bare(tmp_path / "bare.git")
    _git("remote", "add", "origin", str(bare), cwd=str(repo))
    remotes = git_ops.list_remotes(str(repo))
    assert "origin" in remotes
    assert remotes["origin"]["fetch"].endswith("bare.git")


# ===== mirror 集成 =====


def test_mirror_switches_origin_and_keeps_backup(tmp_path):
    from oops.actions import git_ops
    from oops.actions.mirror import cmd_mirror

    # 源仓 -> 推到 origin.git(扮演 GitHub)
    src, _ = _make_repo(tmp_path / "src", ["c1"])
    origin_bare = _make_bare(tmp_path / "origin.git")
    _git("push", str(origin_bare), "main", cwd=str(src))

    # 工作克隆(初始 origin = origin.git,即“GitHub”)
    work = tmp_path / "work"
    _git("clone", str(origin_bare), str(work))
    _cfg_identity(work)

    # 镜像 bare(扮演 CNB)
    cnb_bare = _make_bare(tmp_path / "cnb.git")
    _git("push", str(cnb_bare), "main", cwd=str(src))

    args = Namespace(path=str(work), url=str(cnb_bare), to="cnb", no_verify=True)
    rc = cmd_mirror(args)
    assert rc == 0

    # origin 已切到 cnb
    assert git_ops.get_remote_url(str(work), "origin") == str(cnb_bare)
    # 旧 origin 保留为 github 备份
    assert git_ops.remote_exists(str(work), "github") is True
    assert git_ops.get_remote_url(str(work), "github") == str(origin_bare)


# ===== sync 集成 =====


def _prep_work_behind(tmp_path):
    """返回 (work_path, c1, c2):work 落后 origin 一个提交。"""
    src, shas = _make_repo(tmp_path / "src", ["c1"])
    c1 = shas[0]
    origin_bare = _make_bare(tmp_path / "origin.git")
    _git("push", str(origin_bare), "main", cwd=str(src))

    work = tmp_path / "work"
    _git("clone", str(origin_bare), str(work))
    _cfg_identity(work)
    # 显式设置 origin/HEAD -> main
    _git(
        "symbolic-ref",
        "refs/remotes/origin/HEAD",
        "refs/remotes/origin/main",
        cwd=str(work),
    )

    # 源仓新增 c2 并推到 origin
    _git("commit", "--allow-empty", "-m", "c2", cwd=str(src))
    c2 = _git("rev-parse", "--short", "HEAD", cwd=str(src)).stdout.strip()
    _git("push", str(origin_bare), "main", cwd=str(src))
    return work, c1, c2


def test_sync_aligns_and_backs_up(tmp_path):
    from oops.actions import git_ops
    from oops.actions.sync import cmd_sync

    work, c1, c2 = _prep_work_behind(tmp_path)
    assert git_ops.get_short_sha(str(work)) == c1

    args = Namespace(
        path=str(work),
        remote="origin",
        branch=None,
        no_clean=False,
        no_backup=False,
    )
    rc = cmd_sync(args)
    assert rc == 0

    # 已对齐到 c2
    assert git_ops.get_short_sha(str(work)) == c2
    # 存在备份分支
    branches = _git("branch", "--list", "oops-backup-*", cwd=str(work)).stdout
    assert "oops-backup-" in branches


def test_sync_dirty_stashes(tmp_path):
    from oops.actions import git_ops
    from oops.actions.sync import cmd_sync

    work, _c1, c2 = _prep_work_behind(tmp_path)
    # 制造未跟踪改动
    (work / "scratch.txt").write_text("hello", encoding="utf-8")
    assert git_ops.is_dirty(str(work)) is True

    args = Namespace(
        path=str(work),
        remote="origin",
        branch=None,
        no_clean=False,
        no_backup=False,
    )
    rc = cmd_sync(args)
    assert rc == 0

    # 已对齐,工作区干净,改动被 stash
    assert git_ops.get_short_sha(str(work)) == c2
    assert git_ops.is_dirty(str(work)) is False
    stash_list = _git("stash", "list", cwd=str(work)).stdout
    assert "oops-backup-" in stash_list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
