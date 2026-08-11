# OOPS 命令行手册

**OOPS - One-click Operating Pre-check System (一键运行预检系统)**

> 让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly

---

## 📖 文档说明

本文档面向**高级用户和开发者**，详细介绍命令行参数和配置选项。

**如果你是新手用户**，建议先阅读：
- 🚀 **[快速开始](QUICKSTART.md)** - 一分钟上手
- 📖 **[用户指南](USER_GUIDE.md)** - 详细使用说明和常见问题

---

## 🚀 快速开始

### 最简单的使用方式

直接运行程序，无需任何参数：

```bash
python oops.py
```

程序会自动：
1. ✅ 检测可用的项目配置
2. ✅ 运行诊断检测
3. ✅ 生成HTML报告
4. ✅ 在浏览器中打开报告

---

## 📋 命令行参数

### 基础使用

```bash
# 默认运行（推荐）
python oops.py

# 指定项目
python oops.py --project zenless_zone_zero

# 列出所有可用项目
python oops.py --list-projects
```

### 检测模式

```bash
# 快速扫描（仅关键检测）
python oops.py --quick-scan

# 完整扫描（所有检测）
python oops.py --full-scan
```

### 报告选项

```bash
# 生成HTML报告（默认）
python oops.py --report-format html

# 生成JSON报告
python oops.py --report-format json

# 生成Markdown报告
python oops.py --report-format markdown

# 生成所有格式报告
python oops.py --report-format all

# 不生成报告文件
python oops.py --no-report

# 不自动打开浏览器
python oops.py --no-browser

# 指定报告输出目录
python oops.py --output-dir my_reports
```

### 其他选项

```bash
# 详细输出模式（显示调试信息）
python oops.py --verbose

# 显示版本信息
python oops.py --version

# 创建默认配置文件
python oops.py --create-config
```

### 动作子命令(修复器,v0.3.0+)

> 默认无参运行仍是只读预检。下列子命令是**显式调用**的写操作,用于修复绝区零一条龙
> 因 GitHub 慢/不通、blobless 部分克隆回源导致的启动器自更新失败。exe 用户把 `python oops.py` 换成 `oops.exe`。

#### `mirror` —— 切换目标项目 origin 到镜像

```bash
python oops.py mirror                  # 切到 CNB(默认): cnb.cool/OneDragon-Anything/ZenlessZoneZero-OneDragon
python oops.py mirror --to github      # 切回 GitHub
python oops.py mirror --to gitee       # 切到 Gitee
python oops.py mirror --url <URL>      # 自定义目标 URL
python oops.py mirror --path <目录>     # 指定项目路径(默认自动检测)
python oops.py mirror --no-verify      # 跳过 fetch 可达性验证
```

旧 origin 会被改名为 `github` 备份(可回退),不触碰个人 fork 远程。

#### `sync` —— 对齐到远程 HEAD(硬重置 + 自动备份)

```bash
python oops.py sync                    # 默认对齐 origin/HEAD
python oops.py sync --remote origin    # 指定远程
python oops.py sync --branch main      # 指定分支
python oops.py sync --path <目录>       # 指定项目路径
python oops.py sync --no-clean         # 不执行 git clean -fd
python oops.py sync --no-backup        # 不创建备份(危险:本地改动会丢失)
```

执行流程:`fetch` → 打备份分支 `oops-backup-<时间戳>`(+ 工作区有改动时再 `stash push -u`)→ `reset --hard <remote>/HEAD` → `clean -fd`。
恢复:`git reset --hard oops-backup-<时间戳>` / `git stash pop`。
blobless 部分克隆在 origin 切到完整 CNB 镜像后,`reset` 时按需从 CNB 拉 blob,自愈。

#### `self-update` —— 更新 OOPS 自身

```bash
python oops.py self-update --check     # 仅检查版本
python oops.py self-update             # exe: 下载最新 release 替换;源码: git pull
python oops.py self-update --url <zip> # 指定 zip 直链(可用 CNB 镜像 zzz1d/oops)
python oops.py self-update --force     # 即使已是最新也强制更新
```

exe 模式下,Windows 会先把当前 `oops.exe` 重命名为 `oops.exe.old`(下次启动清理),再写入新版。

> 📦 CNB 镜像制作见 [`cnb/README.md`](cnb/README.md)。

---

## 🎯 常见使用场景

### 场景1：日常检测

```bash
# 一键检测，自动打开报告
python oops.py
```

### 场景2：CI/CD集成

```bash
# 生成JSON报告，不打开浏览器
python oops.py --report-format json --no-browser
```

### 场景3：调试问题

```bash
# 详细输出模式，查看所有日志
python oops.py --verbose
```

### 场景4：多项目检测

```bash
# 快速扫描所有项目
python oops.py --quick-scan
```

### 场景5：首次使用

```bash
# 创建默认配置文件
python oops.py --create-config

# 查看可用项目
python oops.py --list-projects

# 运行检测
python oops.py
```

---

## 📊 报告说明

### HTML报告（推荐）

- **优点**：可视化效果好，易于阅读
- **用途**：日常检测、问题排查
- **自动打开**：检测完成后自动在浏览器中打开

### JSON报告

- **优点**：结构化数据，易于解析
- **用途**：CI/CD集成、自动化处理
- **示例**：
  ```json
  {
    "project": "zenless_zone_zero",
    "timestamp": "2024-01-19T12:00:00",
    "summary": {
      "total_checks": 3,
      "completed": 3,
      "success_rate": 100.0
    }
  }
  ```

### Markdown报告

- **优点**：纯文本，易于版本控制
- **用途**：文档归档、问题记录
- **位置**：`reports/` 目录

---

## ⚙️ 配置文件

### 主配置文件

位置：`configs/oops_master.yaml`

```yaml
version: '1.0'

projects:
  zenless_zone_zero:
    enabled: true
    config: 'configs/zenless_zone_zero.yaml'
    description: '绝区零一条龙项目'

settings:
  default_report_format: 'html'
  log_level: 'INFO'
  max_concurrent_checks: 5
```

### 项目配置文件

位置：`configs/zenless_zone_zero.yaml`

```yaml
project:
  name: '绝区零一条龙'
  type: 'game_script'
  paths:
    install_path: 'D:/ZZZ-OD'

checks:
  network:
    enabled: true
  environment:
    enabled: true
  paths:
    enabled: true
```

---

## 🔧 故障排除

### 问题1：找不到配置文件

**解决方案**：
```bash
# 创建默认配置
python oops.py --create-config
```

### 问题2：检测失败

**解决方案**：
```bash
# 使用详细模式查看错误
python oops.py --verbose
```

### 问题3：报告无法打开

**解决方案**：
```bash
# 手动打开报告文件
# 报告位置：reports/oops_report_项目名_时间戳.html
```

### 问题4：网络检测超时

**解决方案**：
- 检查网络连接
- 关闭代理/VPN
- 使用镜像源

---

## 💡 最佳实践

### 1. 定期检测

建议每周运行一次完整检测：
```bash
python oops.py --full-scan
```

### 2. 保存报告

重要的检测报告建议备份：
```bash
# 生成所有格式报告
python oops.py --report-format all
```

### 3. 自定义配置

根据实际需求修改配置文件：
- 调整检测项目
- 设置超时时间
- 配置镜像源

### 4. CI/CD集成

在自动化流程中使用：
```bash
# 生成JSON报告，不打开浏览器
python oops.py --report-format json --no-browser

# 检查退出码
if [ $? -eq 0 ]; then
    echo "检测通过"
else
    echo "检测失败"
fi
```

---

## 📞 获取帮助

```bash
# 查看完整帮助信息
python oops.py --help

# 查看版本信息
python oops.py --version
```

---

## 📖 相关文档

### 用户文档
- 🏠 **[返回主页](README.md)** - 项目介绍
- 🚀 **[快速开始](QUICKSTART.md)** - 一分钟上手
- 📖 **[用户指南](USER_GUIDE.md)** - 详细使用说明（推荐新手）
- 📝 **[更新日志](CHANGELOG.md)** - 版本历史

### 开发者文档
- 🔧 **[开发者指南](docs/dev/DEVELOPER_GUIDE.md)** - 参与开发
- 📋 **[发布指南](docs/dev/RELEASE_GUIDE.md)** - 版本发布
- 📚 **[文档索引](docs/README.md)** - 完整文档列表
