# CNB 镜像制作与维护

本目录用于把 **OneDragon(绝区零一条龙)** 和 **OOPS** 镜像到 [CNB(cnb.cool)](https://cnb.cool),
解决国内从 GitHub clone/pull 慢、以及 OneDragon 启动器自更新因回源 GitHub 而失败的问题。

## 镜像目标

| 项目 | GitHub 源 | CNB 镜像 | 用途 |
|---|---|---|---|
| OneDragon | `github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon` | `cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon` | `oops mirror` / `oops sync` 的拉取源 |
| OOPS | `github.com/idk500/OOPS` | `cnb.cool/zzz1d/oops` | `oops self-update` 的拉取源 |

> 两个镜像仓都建议设为**公开**,这样终端用户 clone / `oops mirror` 都**无需令牌**。
> 令牌只用于下面「建立镜像」的一次性推送和定时同步。

---

## 一、建立 CNB 仓库(网页操作)

到 https://cnb.cool/org/new 建组织与空公开仓:

- 组织 `OneDragon-Anything` → 仓 `ZenlessZoneZero-OneDragon`
- 组织 `zzz1d` → 仓 `oops`
- (可选,用于定时同步)组织 `zzz1d` → 仓 `sync-onedragon`

## 二、准备令牌(本地,绝不提交)

在 CNB 个人设置里生成一个**有仓库写权限**的访问令牌,写入本目录的 `.cnb-token`(已被 `.gitignore` 忽略):

```bash
# 仅为本地使用,文件不会被 git 跟踪
printf '你的令牌' > cnb/.cnb-token
```

或在 shell 里临时导出:

```bash
export CNB_TOKEN='你的令牌'
```

> CNB 推送凭据:用户名 `cnb`,密码/令牌即上述值。下文用 `$CNB_TOKEN` 代指。

## 三、一次性全量镜像推送

> **现状(2026-08-11)**:OneDragon 的 CNB 镜像已存在且与上游 GitHub 完全同步
> (HEAD 一致),通常**无需手动推送**;OOPS 的镜像 `zzz1d/oops` 已建立(`main` + 全部 tag)。
> 下列命令用于首次初始化或手动刷新。

> 本仓库(OneDragon)**不使用 Git LFS**,因此无需 `git lfs fetch`。
> 镜像源优先用上游官方 GitHub;**国内 GitHub 不通时,改用 Gitee 镜像源**(下方注释)。

```bash
# ---- OneDragon ----
mkdir -p /tmp/m-zzz && cd /tmp/m-zzz
git clone --mirror https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git repo.git
# 国内 GitHub 不通时改用: git clone --mirror https://gitee.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git repo.git
cd repo.git
git push --mirror "https://cnb:${CNB_TOKEN}@cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"

# ---- OOPS ----
# 国内 GitHub 常被重置,直接用 Gitee 源更稳: https://gitee.com/idk500/OOPS.git
mkdir -p /tmp/m-oops && cd /tmp/m-oops
git clone --mirror https://gitee.com/idk500/OOPS.git repo.git
cd repo.git
# 用 refspec 推送(heads+tags),避免 CNB 拒绝 GitHub/Gitee 的 refs/pull/* 合成引用
git push "https://cnb:${CNB_TOKEN}@cnb.cool/zzz1d/oops.git" 'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'
```

`git push --mirror` 会覆盖目标仓所有引用(分支/标签等)。**仅对新建的空仓或你拥有的镜像仓执行**。
OOPS 段改用 refspec(而非 `--mirror`)是为了跳过 `refs/pull/*`——CNB 的 hook 会拒绝这些 GitHub 合成引用。

## 四、持续同步(定时跟随上游)

把本目录的 `.cnb.yml.template` 重命名为 `.cnb.yml`,推送到「同步驱动仓」`zzz1d/sync-onedragon` 的 main 分支:

1. 在该仓 **设置 → 密钥/变量** 添加 `CNB_PUSH_TOKEN`(对镜像仓有写权限的令牌)。
2. 推送 `.cnb.yml`。CNB 会按 `crontab: 0 * * * *`(每小时)自动拉取上游并 force-push 到镜像仓。

> 语法参考: [CNB 定时任务](https://docs.cnb.cool/zh/build/crontab.html)、[配置文件](https://docs.cnb.cool/zh/build/configuration.html)。
> 若 `env`/`$CNB_PUSH_TOKEN` 注入语法与 CNB 最新文档不符,以官方文档为准微调。
> 也可改用 CNB 官方 [git-sync 插件](https://docs.cnb.cool/zh/plugins.html) 实现等价同步。

OOPS 镜像(`zzz1d/oops`)体量小、更新不频繁,可手动重跑上面第三步的 OOPS 段即可,或复制一份 `.cnb.yml` 改指向 OOPS。

## 五、在 OOPS 工具中使用

镜像建好后,终端用户**无需令牌**即可使用(镜像公开):

```bash
# 1) 把游戏项目 origin 切到 CNB(修启动器自更新)
oops mirror                       # 默认 --to cnb

# 2) 对齐到最新 HEAD
oops sync

# 3) 更新 OOPS 自身(从 GitHub release;如要更稳可用 --url 指向 CNB 副本)
oops self-update --check
oops self-update
```

源码运行 OOPS 时,自更新可从 CNB 镜像拉:

```bash
# 在 OOPS 源码仓里加一个 CNB remote(一次性)
git remote add cnb https://cnb.cool/zzz1d/oops.git
oops self-update --remote cnb
```
