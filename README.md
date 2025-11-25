# OOPS  
*One-click Operating Pre-check System*  
*一键运行预检系统*

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)  |   [![Python](https://img.shields.io/badge/python-≥3.8-blue)](https://python.org)

> 让游戏脚本运行更顺畅  
> Run Your Game Scripts Smoothly  

一键检测，运行前发现问题 | One-click check, find issues before running

---

## 🚀 快速开始

### 方式1: 下载可执行文件（推荐）

1. **下载** - 从 [Releases](https://github.com/idk500/OOPS/releases) 下载 `oops-windows-x64.zip`
2. **运行** - 将`oops-windows-x64.zip`扔到项目根目录, 例如你的项目根目录是`E:\\Z1D`,则
    放到 `E:\\Z1D\`下, 最后双击 `E:\\Z1D\oops-windows-x64\oops.exe`
3. **选择项目** - 选择要检测的游戏脚本项目, 当前无需选择.
4. **查看报告** - 自动生成HTML报告并在浏览器中打开

### 方式2: 使用Python运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行检测
python oops.py
```

---

## ✨ 主要功能

### 🔍 全面检测
- **系统信息** - CPU、内存、磁盘、GPU、显示设置
- **硬件适配** - 内存、磁盘类型、用户名、分辨率验证
- **网络连通性** - Git仓库、PyPI源、镜像站点
- **环境依赖** - Python版本、虚拟环境、系统库
- **路径规范** - 中文路径、特殊字符、权限检查
- **🆕 项目版本** - 本地/远程版本比对、启动器版本检测、自动更新建议
- **🆕 游戏设置** - 游戏配置文件检测、启动项验证

### 📊 智能报告
- **HTML格式** - 美观的可视化报告
- **中文界面** - 所有检测项中文显示
- **问题分级** - 错误、警告、信息分类
- **修复建议** - 针对性的解决方案

### 🎯 特色检测
- **HDR检测** - Windows HDR状态检测
- **分辨率验证** - 检查是否满足1920x1080最低要求
- **夜间模式检测** - 护眼模式/颜色滤镜检测
- **磁盘类型** - HDD/SSD识别，建议使用SSD

---

## 📖 文档导航

### 用户文档
- 🚀 **[快速开始](QUICKSTART.md)** - 一分钟上手指南
- 📖 **[用户指南](USER_GUIDE.md)** - 详细使用说明（推荐新手阅读）
- ⚙️ **[命令行手册](USAGE.md)** - 命令行参数和高级用法
- 📝 **[更新日志](CHANGELOG.md)** - 版本更新历史

### 开发者文档
- 🔧 **[开发者指南](docs/dev/DEVELOPER_GUIDE.md)** - 如何参与开发
- 📋 **[发布指南](docs/dev/RELEASE_GUIDE.md)** - 版本发布流程
- 🤖 **[CI/CD 文档](docs/dev/GITHUB_ACTIONS.md)** - 自动化构建说明
- 📚 **[文档索引](docs/README.md)** - 完整文档列表

---

## 🎮 支持的项目

目前支持以下游戏脚本项目：

| 项目 | 配置文件 | 状态 |
|------|----------|------|
| 绝区零自动化脚本 | `zenless_zone_zero.yaml` | ✅ 已支持 |
| 更多项目 | 敬请期待 | 🚧 开发中 |

---

## 💡 常见问题

### Q: 检测需要多长时间？
A: 通常3-5秒完成所有检测。

### Q: 需要联网吗？
A: 网络检测需要联网，其他检测可离线进行。

### Q: 支持哪些操作系统？
A: 主要支持Windows，Linux和macOS部分功能可用。

### Q: 检测会修改我的系统吗？
A: 不会。OOPS只进行检测，不会修改任何系统设置。后续也许会增加修复器，在用户监视下协助修复。

---

## 🤝 参与贡献

欢迎贡献代码、文档或提出建议！

- 🐛 **报告问题**：[GitHub Issues](https://github.com/idk500/OOPS/issues)
- 💡 **功能建议**：[GitHub Discussions](https://github.com/idk500/OOPS/discussions)
- 🔧 **贡献代码**：查看 [开发者指南](docs/dev/DEVELOPER_GUIDE.md)

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢所有为开源项目提供问题反馈和解决方案的社区成员！

---

**OOPS - 让游戏脚本运行更顺畅！**  
**OOPS - Run Your Game Scripts Smoothly!**
