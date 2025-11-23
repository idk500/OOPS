# OOPS v1.0.0 发布说明

**发布日期**: 2025-11-22

## 🎉 首个正式版本

OOPS (One-click Operating Pre-check System) 是一个专为游戏脚本项目设计的诊断工具，帮助用户在运行脚本前检测和解决潜在问题。

## ✨ 核心功能

### 1. 系统信息检测
- CPU、内存、磁盘、GPU信息收集
- 操作系统和Python环境检测
- 跨平台支持（Windows/Linux/macOS）

### 2. 硬件适配检测
- **内存验证**: 检查是否满足最低8GB要求
- **磁盘类型检测**: 识别HDD/SSD，建议使用SSD
- **用户名规范**: 检测中文、特殊字符等问题
- **显示器分辨率**: 验证是否满足1920x1080最低要求

### 3. 显示设置检测
- **HDR检测**: Windows HDR状态检测
- **夜间模式**: 护眼模式/夜间模式检测
- **颜色滤镜**: Windows颜色滤镜检测
- **分辨率验证**: 跨平台分辨率检测和验证

### 4. 网络连通性检测
- Git仓库连通性（GitHub/Gitee）
- PyPI源可用性检测
- GitHub代理检测
- 项目官网和API检测
- 智能超时和重试机制

### 5. 环境依赖检测
- Python版本验证
- 虚拟环境检测
- 系统运行库检测（MSVC、DirectX、.NET Framework）
- 项目依赖包检测

### 6. 路径规范检测
- 中文路径检测
- 特殊字符检测
- 路径长度验证
- 权限检查

## 📊 报告系统

### HTML报告
- 美观的HTML格式报告
- 支持折叠/展开详情
- 深色模式支持
- 响应式设计

### 中文化界面
- 所有检测项中文显示
- 清晰的问题分类
- 详细的修复建议

### 智能展示
- 通过项默认折叠
- 问题项自动展开
- 按严重程度排序

## 🚀 使用方法

### 基本使用
```bash
python oops.py
```

### 指定项目
```bash
python oops.py --project zenless_zone_zero
```

### 不打开浏览器
```bash
python oops.py --no-browser
```

## 📦 安装

### 依赖安装
```bash
pip install -r requirements.txt
```

### 开发依赖
```bash
pip install -r requirements-dev.txt
```

## 🔧 配置

### 项目配置
在 `configs/` 目录下创建项目配置文件：
```yaml
project:
  name: '项目名称'
  type: 'game_script'
  
checks:
  system_info:
    enabled: true
  network:
    enabled: true
  environment:
    enabled: true
  paths:
    enabled: true
```

## 📚 文档

- **用户指南**: [USER_GUIDE.md](USER_GUIDE.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **使用说明**: [USAGE.md](USAGE.md)
- **架构文档**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

## 🎯 支持的项目

目前支持：
- 绝区零一条龙 (ZenlessZoneZero-OneDragon)

可通过配置文件扩展支持更多项目。

## 🔨 构建

### 打包为可执行文件
```bash
cd build/scripts
./build.bat  # Windows
./build.sh   # Linux/macOS
```

## 🐛 已知问题

1. Windows下asyncio可能产生警告（不影响功能）
2. 某些Linux发行版需要安装xrandr才能检测分辨率

## 🙏 致谢

感谢所有测试用户的反馈和建议！

## 📝 许可证

本项目采用 MIT 许可证。

---

**下载**: [GitHub Releases](https://github.com/idk500/OOPS/releases/tag/v1.0.0)

**反馈**: [提交Issue](https://github.com/idk500/OOPS/issues)
