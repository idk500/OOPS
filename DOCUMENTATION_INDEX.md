# OOPS 项目文档索引

## 📚 文档概览

本文档索引提供了OOPS项目的完整文档结构，方便开发者快速找到所需信息。

## 🏗️ 核心文档

### 项目说明
- [`README.md`](README.md) - 项目简介、快速开始、使用指南
  - 项目背景和功能概述
  - 快速安装和运行指南
  - 配置文件和项目选择

### 功能规划
- [`FEATURE_LIST.md`](FEATURE_LIST.md) - 完整功能清单
  - 9大核心功能模块详细说明
  - 硬件配置检测功能
  - 多项目支持架构

### 开发指南
- [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) - 开发者入门指南
  - 环境准备和项目设置
  - 代码规范和开发工作流
  - 核心开发概念和API参考

## 🎯 架构设计文档

### 项目结构
- [`project_structure.md`](project_structure.md) - 项目架构和文件结构
  - 完整的项目目录结构
  - 模块职责划分
  - 代码组织原则

### 功能设计
- [`functional_design.md`](functional_design.md) - 功能模块详细设计
  - 核心功能模块设计
  - 检测器系统架构
  - 配置管理系统

### 多项目架构
- [`multi_project_architecture.md`](multi_project_architecture.md) - 多项目支持架构
  - 分层配置系统设计
  - 项目配置文件结构
  - 完整的项目文件树

## 🔧 技术实现文档

### 检测系统设计

#### Git检测系统
- [`unified_git_detection.md`](unified_git_detection.md) - Git统一检测系统设计
  - 多Git客户端支持（pygit2、gitpython、命令行）
  - 自动降级和错误处理
  - 性能监控和配置管理

#### 虚拟环境检测
- [`virtualenv_detection.md`](virtualenv_detection.md) - 虚拟环境检测系统设计
  - 多环境类型支持（venv、conda、pipenv等）
  - 依赖分析和健康检查
  - 自动修复建议

#### 游戏设置检测
- [`game_setting_detection.md`](game_setting_detection.md) - 游戏设置检测实现
  - 游戏设置检测基础架构
  - 导航步骤和验证规则
  - 配置模板和示例

### 高级功能设计

#### YOLO回退机制
- [`game_setting_yolo_fallback.md`](game_setting_yolo_fallback.md) - 游戏设置检测的YOLO回退机制设计
  - 多策略检测系统（YOLO、图像识别、坐标回退）
  - 自动降级和性能优化
  - 错误处理和配置灵活

#### YAML配置模板
- [`game_setting_yaml_template.md`](game_setting_yaml_template.md) - 游戏设置检测YAML配置模板
  - 完整的配置结构定义
  - 多游戏项目配置示例
  - 高级配置选项和验证

#### SSL证书修复
- [`ssl_certificate_repair.md`](ssl_certificate_repair.md) - SSL证书检测和自动修复功能设计
  - 基于debug.bat的SSL修复经验转化
  - Git SSL后端自动配置
  - 系统证书完整性检测和修复
  - 网络SSL连接测试和故障排除

## 🗂️ 知识库和参考资料

### 项目知识库
- [`knowledge_base/zenless_zone_zero_knowledge.md`](knowledge_base/zenless_zone_zero_knowledge.md) - 绝区零一条龙知识库
  - 基于历史客服问题总结
  - 网络连通性配置
  - 常见问题解决方案
  - 硬件配置要求

### 参考文件
- [`dev/ref/sample.txt`](dev/ref/sample.txt) - 客服问题总结（原始数据）
- [`dev/ref/connectivity_test_report.json`](dev/ref/connectivity_test_report.json) - 网络连通性测试报告
- [`dev/ref/debug.bat`](dev/ref/debug.bat) - 调试脚本参考

### 开发文档
- [`dev/dev.md`](dev/dev.md) - 原始开发计划（半成品）
- [`审批意见.md`](审批意见.md) - 项目审批反馈和改进要求

## 🔄 文档更新日志

### 最近更新
- **2024-01-19**: 完成多项目架构文档和文件树补充
- **2024-01-19**: 创建完整的文档索引
- **2024-01-19**: 完善游戏设置检测YAML配置模板
- **2024-01-19**: 设计YOLO回退机制
- **2024-01-19**: 添加虚拟环境和Git检测系统设计

### 待完成文档
- [ ] 游戏窗口大小变化问题处理（TBD）
- [ ] 性能优化指南
- [ ] 部署和运维手册
- [ ] API参考文档

## 🚀 快速导航

### 新用户入门
1. 阅读 [`README.md`](README.md) 了解项目
2. 查看 [`FEATURE_LIST.md`](FEATURE_LIST.md) 了解功能
3. 按照 [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) 设置开发环境

### 开发者扩展
1. 学习 [`multi_project_architecture.md`](multi_project_architecture.md) 架构设计
2. 参考 [`unified_git_detection.md`](unified_git_detection.md) 添加新检测器
3. 使用 [`game_setting_yaml_template.md`](game_setting_yaml_template.md) 配置新项目

### 配置管理
1. 主配置: [`configs/oops_master.yaml`](configs/oops_master.yaml)（模板）
2. 项目配置: [`projects/_template.yaml`](projects/_template.yaml)
3. 检测配置: 各模块的YAML配置文件

## 📖 文档编写规范

### 文档结构
- 使用清晰的标题层级
- 包含代码示例和配置模板
- 提供实际使用场景
- 包含故障排除指南

### 代码示例
- 使用正确的语法高亮
- 提供完整的可运行示例
- 包含必要的导入和依赖说明

### 配置模板
- 提供完整的YAML配置结构
- 包含注释说明每个配置项
- 提供不同场景的配置示例

## 🔍 搜索指南

### 按功能搜索
- **网络检测**: 查看 [`unified_git_detection.md`](unified_git_detection.md)
- **环境检测**: 查看 [`virtualenv_detection.md`](virtualenv_detection.md)
- **游戏设置**: 查看 [`game_setting_detection.md`](game_setting_detection.md)

### 按技术搜索
- **YOLO**: 查看 [`game_setting_yolo_fallback.md`](game_setting_yolo_fallback.md)
- **配置管理**: 查看 [`multi_project_architecture.md`](multi_project_architecture.md)
- **Git集成**: 查看 [`unified_git_detection.md`](unified_git_detection.md)

### 按项目搜索
- **绝区零**: 查看 [`knowledge_base/zenless_zone_zero_knowledge.md`](knowledge_base/zenless_zone_zero_knowledge.md)
- **MAA明日方舟**: 参考项目配置模板
- **鸣潮**: 参考项目配置模板

## 💡 贡献指南

### 文档贡献
1. 遵循现有的文档结构
2. 提供实际的使用示例
3. 包含故障排除内容
4. 更新文档索引

### 代码贡献
1. 参考 [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md)
2. 遵循代码规范
3. 添加相应的测试用例
4. 更新相关文档

---

**最后更新**: 2024-01-19  
**维护者**: OOPS开发团队  
**文档状态**: 完整 ✅

> 如有文档问题或建议，请提交Issue或Pull Request。