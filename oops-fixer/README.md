# OneDragon-Oops 兜底修复器

这是独立版 OneDragon-Oops,用于放在 ZenlessZoneZero-OneDragon 项目根目录双击急救。

## 功能

- 检测是否在项目根目录运行。
- 自动检测并修复不可用的 PyPI 源。
- 将代码 remote 固定到 CNB,强制恢复到 `main` 最新版本。
- **虚拟环境体检与修复**:`.venv` 缺失/损坏(python.exe 缺失、基础 Python 被卸载)/
  版本与项目要求不符(不同版本启动器留下的遗留形态)时,用项目自带 uv 按启动器的方式
  重建(`uv venv --python=<project.yml 版本> --no-python-downloads` + `uv sync`,
  本地 wheels 优先);修复前自动备份旧环境,失败自动回滚。
- **按文件名更新启动器**:存在 `OneDragon-Launcher.exe` → 更新原始版;
  存在 `OneDragon-RuntimeLauncher.exe` → 更新集成版(自带运行时),各对应 CNB 上不同的包。
  两个都在时用 `.venv` 决胜;旧 exe 备份 `.bak`。
- 完成后打开 oops 页面和对应形态的启动器(缺失时自动回退另一种)。
- **成功即清理日志**:急救全部成功后删除 `OneDragon-Oops.log`(日志存在 = 上次失败)。
- **完全重置(无脑重置)**:启动时若发现上次失败的日志,自动下载最新全量环境包
  (约 700MB,自动探测最新版本号,404 回退旧版本),解压到新目录
  `<旧目录名>_月日`(如 `D:\ZZZ1D_0819`;同日已重置成功过则拒绝,防止误删在用目录),
  迁移用户配置与最多两个账户目录(`config/01`、`config/02`,`env.yml` 内绝对路径自动改写为新目录),
  拷贝本工具到新目录并从新目录启动。旧目录原样保留。

## 构建

```powershell
uv sync --group dev
cd deploy
..\.venv\Scripts\pyinstaller.exe --noconfirm --clean OneDragon-Oops.spec
```

产物:

`dist\OneDragon-Oops.exe`
