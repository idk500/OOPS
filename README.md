# OOPS  
*One-click Operating Pre-check System*  
*一键运行预检系统*

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)  
[![Python](https://img.shields.io/badge/python-≥3.8-blue)](https://python.org)

> 让游戏脚本运行更顺畅  
> Run Your Game Scripts Smoothly  
> 
> 一键检测，运行前发现问题  
> One-click check, find issues before running

---

## 🚀 快速开始 (用户版)

### 最简单的方式 - 一键运行！
1. **下载 OOPS** - 从 [Release页面](https://github.com/idk500/OOPS/releases) 下载 `oops.exe`
2. **双击运行** - 直接双击 `oops.exe` 文件
3. **选择项目** - 在弹出的窗口中选择你要检测的项目：
   - 🎮 绝区零自动化脚本
   - [TBD]⚔️ 明日方舟助手  
   - [TBD]🌊 鸣潮自动化脚本
   - [TBD]🔧 其他游戏脚本项目...
4. **查看报告** - 等待检测完成，查看生成的HTML报告

### 使用预置配置模板
OOPS 提供了多个预置配置模板，开箱即用：

| 项目 | 配置文件 | 检测内容 |
|------|----------|----------|
| 绝区零一条龙 | `configs/zenless_zone_zero.yaml` | 网络、环境、路径、游戏设置 |
| [TBD]MAA明日方舟助手 | `configs/maa_assistant_arknights.yaml` | 网络、环境、路径、游戏设置 |
| [TBD]OK鸣潮脚本 | `configs/ok_wuthering_waves.yaml` | 网络、环境、路径 |
| 通用Python项目 | `configs/generic_python.yaml` | 网络、环境、虚拟环境 |

### 命令行使用 (高级用户)
```bash
# 默认运行（自动检测并打开报告）
oops.exe

# 指定项目检测
oops.exe --project zenless_zone_zero

# 不自动打开浏览器
oops.exe --no-browser

# 详细输出模式
oops.exe --verbose

# 生成JSON格式报告
oops.exe --report-format json
```

---

## 🛠️ 开发者快速入门

### 环境准备
```bash
# 1. 克隆项目
git clone https://github.com/your-username/OOPS.git
cd OOPS

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# 3. 安装依赖
pip install -r requirements-dev.txt
pip install -e .
```

### 开发测试
```bash
# 运行测试
pytest tests/

# 代码格式化
black oops/
isort oops/

# 类型检查
mypy oops/
```

### 添加新项目配置
1. 复制项目模板：
```bash
oops --create-project my_new_project --name "我的新项目" --type game_script
```

2. 编辑 `projects/my_new_project.yaml` 配置文件

3. 在主配置中启用项目：
```yaml
# oops_master.yaml
projects:
  my_new_project:
    enabled: true
    config: "projects/my_new_project.yaml"
```

### 核心开发文档
- **文档索引**: [`DOCUMENTATION_INDEX.md`](docs/dev/DOCUMENTATION_INDEX.md) - 完整文档导航
- **架构设计**: [`project_structure.md`](docs/dev/project_structure.md) - 项目结构和核心文件
- **功能设计**: [`FEATURE_LIST.md`](docs/dev/FEATURE_LIST.md) - 完整功能列表
- **实施计划**: [`IMPLEMENTATION_PLAN.md`](docs/dev/IMPLEMENTATION_PLAN.md) - 分阶段实施计划
- **多项目支持**: [`multi_project_architecture.md`](docs/dev/multi_project_architecture.md) - 多项目架构
- **游戏检测**: [`game_setting_yolo_fallback.md`](docs/dev/game_setting_yolo_fallback.md) - 游戏设置检测

---

## What is it? | 项目简介

OOPS is a lightweight, **open-source diagnostic toolbox** for Windows gamers and developers.  
OOPS 是一款轻量级、**开源的诊断工具箱**，面向 Windows 玩家与开发者。  

One click (or one command) and it checks:  
只需点击（或一条命令）即可检查：

| Category | English | 中文 |
|----------|---------|------|
| Network | connectivity to patch/CDN/lobby servers | 网络连通性（补丁/CDN/大厅服务器） |
| Runtime deps | MSVC, DirectX, .NET, Vulkan, OpenSSL... | 运行库依赖 |
| Env vars | PATH, JAVA_HOME, STEAM... | 环境变量 |
| Game configs | .ini, launch flags, anti-cheat | 游戏设置与反作弊 |
| Registry | install paths, DLC flags | 注册表键值 |
| Hardware | free RAM/disk, GPU temp, driver date | 硬件健康 |

Everything is **offline-first** – no telemetry, no cloud, 100 % local logs.  
全程**离线优先**——无遥测、无云、日志 100% 本地。

---

## Features | 核心功能

### 🔍 全面检测覆盖
- **网络连通性检测** - Git仓库、PyPI源、镜像源、项目官网
- **环境依赖检测** - Python环境、系统运行库、驱动程序
- **工程目录检测** - 路径规范、权限检查、中文路径识别
- **脚本运行环境** - 虚拟环境、依赖包、配置文件
- **硬件健康检查** - 内存、磁盘、GPU温度、驱动程序

### 🛠️ 智能问题诊断
- 基于历史问题库的智能匹配
- 自动识别常见错误模式
- 提供针对性解决方案
- 生成详细诊断报告

### 📊 可视化报告
- HTML/JSON格式报告输出
- 实时检测进度显示
- 问题严重程度分级
- 一键修复建议

### 🎮 游戏设置检测 (TBD)
- 自动化游戏设置导航
- 多模式识别（YOLO/图像/坐标）
- 设置值验证和推荐
- 窗口自适应处理

---

## Quick start | 快速开始

### 对于最终用户
```bash
# 最简单的方式 - 双击 oops.exe 并选择项目
# 或者使用命令行选择项目
oops.exe --project zenless_zone_zero
```

### 对于开发者
```bash
# 开发环境设置
git clone https://github.com/your-username/OOPS.git
cd OOPS
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# 运行开发版本
python oops.py --project zenless_zone_zero --verbose
```

### 配置文件示例
OOPS 提供预置配置模板，用户无需手动编辑YAML文件。如需自定义，可参考：

```yaml
# configs/zenless_zone_zero.yaml (预置模板)
project:
  name: "绝区零一条龙"
  type: "game_script"
  paths:
    install_path: "D:/ZZZ-OD"

checks:
  network:
    enabled: true
    git_repos:
      - "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"
  environment:
    enabled: true
    python_version: ">=3.8"
```

---

## Usage Examples | 使用示例

### 基本使用
```bash
# 运行完整检测（图形界面）
oops.exe

# 指定项目检测
oops.exe --project zenless_zone_zero

# 生成HTML报告
oops.exe --project maa_assistant_arknights --report html
```

### 检测模块
```python
from oops.core import DiagnosticSuite

# 创建检测套件
diagnostics = DiagnosticSuite(project="zenless_zone_zero")

# 运行检测
results = diagnostics.run_diagnostics()

# 生成报告
report = diagnostics.generate_report()
diagnostics.save_report("diagnostic_report.html")
```

---

## Problem Coverage | 问题覆盖范围

基于历史客服问题总结，OOPS 覆盖以下常见问题：

### 🔧 安装类问题
- Python虚拟环境安装失败
- 依赖包下载超时（WinError 10060/10061）
- SSL证书错误
- 路径包含中文或特殊字符
- 杀毒软件误报
- 权限不足

### 🌐 网络类问题  
- Git仓库连接超时
- PyPI源访问失败
- 镜像源速度测试
- 代理配置错误
- 防火墙阻挡

### ⚙️ 环境类问题
- 缺少运行库（MSVC, DirectX, .NET）
- Python版本不兼容
- 环境变量配置错误
- 虚拟环境损坏
- 驱动程序过时

### 🎮 游戏设置问题
- 分辨率设置错误
- 全屏/窗口模式问题
- 多显示器配置
- 反作弊软件冲突
- 游戏配置文件损坏

---

## Project Structure | 项目结构

```
OOPS/
├── oops.exe                    # 主可执行文件 (用户使用)
├── oops/                       # Python包 (开发者使用)
├── configs/                    # 预置配置模板
├── projects/                   # 项目配置文件
├── docs/                       # 文档
├── tests/                      # 测试代码
└── README.md                   # 项目说明
```

---

## Roadmap | 发展路线

### 🚀 短期目标 (v1.0 - 最小化底座)
- [x] 项目规划和架构设计
- [x] 文档体系建立
- [x] 配置系统设计
- [ ] 基础检测框架实现
- [ ] 网络连通性检测
- [ ] 环境依赖检测
- [ ] 路径规范检查
- [ ] 报告系统实现

### 🔮 中期目标 (v2.0 - 核心功能)
- [ ] 图形化界面开发
- [ ] YOLO模型识别集成
- [ ] 跨项目配置文件适配
- [ ] 自动化修复工具
- [ ] 一键修复功能
- [ ] 知识库系统集成

### 🌟 长期愿景 (v3.0+)
- [ ] 机器学习问题预测
- [ ] 云端知识库同步
- [ ] 多平台支持
- [ ] 插件生态系统
- [ ] 多语言支持

---

## Contributing | 贡献指南

我们欢迎各种形式的贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

1. **报告问题** - 在 Issues 中提交 bug 报告或功能请求
2. **代码贡献** - 提交 Pull Request 改进代码
3. **文档完善** - 帮助改进文档和翻译
4. **测试反馈** - 测试新功能并提供反馈

---

## License | 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## Acknowledgments | 致谢

感谢所有为开源项目提供问题反馈和解决方案的社区成员，特别感谢：

- OneDragon 项目团队的问题经验总结
- MAA项目团队的宝贵经验
- 所有测试和反馈的用户

---

**OOPS - 让问题排查变得简单！**  
**OOPS - Making problem solving easy!**