# OOPS 快速开始

**OOPS - One-click Operating Pre-check System (一键运行预检系统)**

> 让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly

## 🎯 一分钟上手

### 1️⃣ 运行检测

```bash
python oops.py
```

就这么简单！程序会自动：
- ✅ 检测网络连通性
- ✅ 检测环境依赖
- ✅ 检测路径规范
- ✅ 生成HTML报告
- ✅ 在浏览器中打开报告

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `python oops.py` | 默认运行（推荐） |
| `python oops.py --verbose` | 详细输出模式 |
| `python oops.py --no-browser` | 不自动打开浏览器 |
| `python oops.py --list-projects` | 列出所有项目 |
| `python oops.py --help` | 查看帮助 |

---

## 🎨 输出示例

```
[*] 自动运行唯一可用项目: 绝区零一条龙
[*] 开始检测项目: zenless_zone_zero
[*] 检测项目计划:
   +- 基础检测
   +- 网络连通性 (2个Git仓库, 3个PyPI源)
   +- 环境依赖 (Python>=3.8, 3个系统库)
   +- 路径规范 (安装路径: D:/ZZZ-OD)
   +- 检测准备完成

[*] 检测完成!
   [+] 成功: 3 项
   [-] 失败: 0 项
   [!] 问题: 3 个
   [%] 成功率: 100.0%

📄 HTML报告已生成: reports\oops_report_zenless_zone_zero_20251121_233917.html
🌐 已在浏览器中打开报告
```

---

## 🔧 首次使用

如果是第一次使用，需要创建配置文件：

```bash
# 1. 创建默认配置
python oops.py --create-config

# 2. 编辑配置文件（可选）
# 修改 configs/zenless_zone_zero.yaml 中的 install_path

# 3. 运行检测
python oops.py
```

---

## 📊 报告位置

所有报告保存在 `reports/` 目录：

```
reports/
├── oops_report_zenless_zone_zero_20251121_233917.html
├── oops_report_zenless_zone_zero_20251121_233917.json
└── oops_report_zenless_zone_zero_20251121_233917.markdown
```

---

## 💡 提示

- 🚀 **无需参数**：直接运行 `python oops.py` 即可
- 🌐 **自动打开**：报告会自动在浏览器中打开
- 📝 **详细日志**：所有日志保存在 `oops.log` 文件
- ⚙️ **灵活配置**：可以自定义检测项目和规则

---

## 📖 下一步

### 新手推荐阅读顺序

1. ✅ **你在这里** → [快速开始](QUICKSTART.md)（当前页面）
2. 📖 **详细指南** → [用户指南](USER_GUIDE.md) - 了解所有功能和使用技巧
3. ⚙️ **高级用法** → [命令行手册](USAGE.md) - 命令行参数和配置选项

### 其他文档

- 🏠 **[项目主页](README.md)** - 项目介绍和功能概览
- 📝 **[更新日志](CHANGELOG.md)** - 版本更新历史
- 🔧 **[开发者指南](docs/dev/DEVELOPER_GUIDE.md)** - 如何参与开发

---

**就是这么简单！开始使用 OOPS 吧！** 🎉
