# OOPS 使用说明

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

**更多信息请参考**：
- [README.md](README.md) - 项目简介
- [DEVELOPER_GUIDE.md](docs/dev/DEVELOPER_GUIDE.md) - 开发者指南
- [FEATURE_LIST.md](docs/dev/FEATURE_LIST.md) - 功能清单
