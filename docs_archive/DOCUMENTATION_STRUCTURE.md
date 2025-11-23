# OOPS 文档结构说明

## 📁 文档组织原则

**面向用户优先** - 主目录保持简洁，面向最终用户；开发者内容通过索引访问。

---

## 📂 主目录（用户文档）

### 核心文档
- **[README.md](../README.md)** - 项目介绍和快速开始
- **[QUICKSTART.md](../QUICKSTART.md)** - 一分钟上手指南
- **[USER_GUIDE.md](../USER_GUIDE.md)** - 详细使用说明
- **[USAGE.md](../USAGE.md)** - 命令行参数说明

### 项目信息
- **[CHANGELOG.md](../CHANGELOG.md)** - 版本更新历史
- **[ROADMAP.md](../ROADMAP.md)** - 未来发展计划
- **[LICENSE](../LICENSE)** - 开源许可证

---

## 📂 docs/ 目录

### docs/ (技术文档)
- **[HDR_DETECTION.md](../HDR_DETECTION.md)** - HDR检测技术说明
- **[GAME_SETTINGS_ANALYSIS.md](GAME_SETTINGS_ANALYSIS.md)** - 游戏设置分析
- **[RESOLUTION_DETECTION.md](RESOLUTION_DETECTION.md)** - 分辨率检测说明

### docs/dev/ (开发者文档)
- **[README_DEV.md](dev/README_DEV.md)** - 开发者文档入口 ⭐
- **[ARCHITECTURE.md](dev/ARCHITECTURE.md)** - 系统架构设计
- **[DEVELOPER_GUIDE.md](dev/DEVELOPER_GUIDE.md)** - 开发者指南
- **[DOCUMENTATION_INDEX.md](dev/DOCUMENTATION_INDEX.md)** - 完整文档索引
- **[FEATURE_LIST.md](dev/FEATURE_LIST.md)** - 功能列表
- **[project_structure.md](dev/project_structure.md)** - 项目结构
- **[multi_project_architecture.md](dev/multi_project_architecture.md)** - 多项目架构
- **[ICON_GUIDE.md](dev/ICON_GUIDE.md)** - 图标使用指南

### docs/dev/ (发布文档)
- **[RELEASE_CHECKLIST_v1.0.0.md](dev/RELEASE_CHECKLIST_v1.0.0.md)** - 发布检查清单
- **[RELEASE_NOTES_v1.0.0.md](dev/RELEASE_NOTES_v1.0.0.md)** - 发布说明
- **[VERSION_SUMMARY.md](dev/VERSION_SUMMARY.md)** - 版本总结
- **[NAME_UPDATE_SUMMARY.md](dev/NAME_UPDATE_SUMMARY.md)** - 名称更新记录

### docs/dev/ (技术文档)
- **[game_setting_yolo_fallback.md](dev/game_setting_yolo_fallback.md)** - 游戏设置检测
- **[game_setting_yaml_template.md](dev/game_setting_yaml_template.md)** - 配置模板
- **[ssl_certificate_repair.md](dev/ssl_certificate_repair.md)** - SSL证书修复
- **[unified_git_detection.md](dev/unified_git_detection.md)** - Git检测
- **[virtualenv_detection.md](dev/virtualenv_detection.md)** - 虚拟环境检测
- **[report_design.md](dev/report_design.md)** - 报告设计

### docs/knowledge_base/ (知识库)
- **[zenless_zone_zero_knowledge.md](knowledge_base/zenless_zone_zero_knowledge.md)** - 绝区零知识库

---

## 📂 build/ 目录（构建文档）

### build/docs/
- **[BUILD.md](../build/docs/BUILD.md)** - 构建说明
- **[BUILD_QUICK_REFERENCE.md](../build/docs/BUILD_QUICK_REFERENCE.md)** - 快速参考
- **[BUILD_SUMMARY.md](../build/docs/BUILD_SUMMARY.md)** - 构建总结
- **[RELEASE_CHECKLIST.md](../build/docs/RELEASE_CHECKLIST.md)** - 发布检查清单

---

## 🎯 文档访问路径

### 用户路径
```
README.md → QUICKSTART.md → USER_GUIDE.md → USAGE.md
```

### 开发者路径
```
README.md → docs/dev/README_DEV.md → 具体开发文档
```

### 技术路径
```
README.md → docs/ → 技术文档
```

---

## 📝 文档维护原则

### 1. 用户优先
- 主目录文档面向最终用户
- 语言简洁，避免技术术语
- 提供清晰的使用示例

### 2. 开发者友好
- 开发者文档集中在 docs/dev/
- 提供完整的技术细节
- 包含代码示例和API说明

### 3. 结构清晰
- 文档分类明确
- 通过索引文档导航
- 避免重复内容

### 4. 保持同步
- 代码更新时同步更新文档
- 版本发布时更新CHANGELOG
- 定期检查文档准确性

---

## 🔄 文档更新流程

### 新功能文档
1. 更新 CHANGELOG.md
2. 更新相关用户文档
3. 添加技术文档（如需要）
4. 更新开发者文档

### 版本发布文档
1. 创建 RELEASE_NOTES_vX.X.X.md
2. 更新 VERSION_SUMMARY.md
3. 更新 ROADMAP.md
4. 更新 README.md（如有重大变化）

---

## 📊 文档统计

### 用户文档
- 主目录: 4个
- 总计: 4个

### 开发者文档
- docs/dev/: 15+个
- build/docs/: 4个
- 总计: 19+个

### 技术文档
- docs/: 3个
- docs/knowledge_base/: 1个
- 总计: 4个

---

## 🎨 文档风格指南

### Markdown格式
- 使用标准Markdown语法
- 代码块指定语言
- 表格对齐整齐
- 链接使用相对路径

### 中英文混排
- 中英文之间加空格
- 专有名词保持原文
- 代码和命令使用英文

### 示例代码
- 提供完整可运行的示例
- 添加必要的注释
- 说明预期输出

---

**文档是项目的重要组成部分，保持文档的准确性和可读性！** 📚
