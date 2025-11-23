# 检测顺序和架构重构进度

## 目标

重组检测顺序，优化报告展示，增强依赖检测功能。

## 新的检测顺序

```
1. 硬件信息 (Hardware) - hardware_info
2. 系统信息 (System) - system_info  
3. 系统设置 (System Settings) - system_settings
4. 网络连通性 (Network) - network_connectivity
5. Python 环境 (Python Environment) - python_environment
6. 组件依赖 (Dependencies) - dependencies
7. 路径规范 (Path Validation) - path_validation
8. 项目配置 (Project Settings) - project_settings
9. 游戏设置 (Game Settings) - game_settings [TBD]
```

## 实施阶段

### 阶段 1：重组检测顺序 ✅

#### 1.1 拆分 system_info 检测器
- [x] 创建 `hardware_detector.py` - 硬件信息收集
- [x] 创建 `system_detector.py` - 系统信息收集
- [x] 创建 `system_settings_detector.py` - 系统设置检测
- [ ] 保留 `system_info_detector.py` 作为协调器（向后兼容）

#### 1.2 创建 python_environment 检测器
- [x] 创建 `python_environment_detector.py`
- [x] 实现包管理器类型识别（pip/conda/uv/poetry/pipenv）
- [x] 实现虚拟环境检测
- [x] 实现依赖完整性检查
- [ ] 移动相关逻辑从 `environment_detector.py`

#### 1.3 更新 DiagnosticSuite
- [x] 修改检测器注册顺序
- [x] 更新检测规则映射
- [x] 确保向后兼容（保留旧的 system_info）

### 阶段 2：优化系统信息展示 ⏳

#### 2.1 修改系统信息模块
- [ ] 系统信息只展示数据，不显示警告
- [ ] 默认折叠详细信息
- [ ] 优化摘要显示

#### 2.2 独立硬件适配检测
- [ ] 从 system_info 中分离硬件适配逻辑
- [ ] 创建独立的 hardware_compatibility 检测项
- [ ] 在检测结果中显示，而不是系统信息中

### 阶段 3：增强 Python 环境检测 ⏳

#### 3.1 包管理器识别
- [ ] 实现 conda/anaconda 检测
- [ ] 实现 uv 检测
- [ ] 实现 pip 检测
- [ ] 实现 poetry/pipenv 检测

#### 3.2 虚拟环境依赖检查
- [ ] 解析 requirements.txt
- [ ] 获取虚拟环境已安装包列表
- [ ] 比对缺失的包
- [ ] 检查版本不匹配
- [ ] 检查依赖冲突

### 阶段 4：完善检测分类 ⏳

#### 4.1 更新报告结构
- [ ] 按新顺序组织 HTML 报告
- [ ] 按新顺序组织 YAML 报告
- [ ] 更新数据模型

#### 4.2 更新文档
- [ ] 更新 README
- [ ] 更新用户指南
- [ ] 更新开发文档

## 当前进度

**开始时间**: 2025-11-23 11:15

**当前阶段**: 阶段 2 - 优化系统信息展示

**当前任务**: 修复问题并完成数据渲染分离

**发现的问题**:
1. ✅ 系统信息显示"收集失败或未执行" - 数据结构不匹配 → 已修复
2. ⏳ 网络连通性检测规则不一致 - 需要统一为通用规则
3. ⏳ HTML 生成耦合在检测器中 - 需要完全解耦

### 2025-11-23 11:45
- ✅ 修复系统信息提取逻辑
- 更新 `_extract_system_info` 方法支持新检测器数据结构
- 将新检测器的数据映射到旧的数据结构（临时方案，保持兼容）

## 变更记录

### 2025-11-23 11:15
- 创建重构进度文档
- 开始阶段 1.1：拆分 system_info 检测器

### 2025-11-23 11:20
- ✅ 创建 `hardware.py` - 纯硬件信息收集（CPU、内存、GPU、存储）
- 特点：只收集数据，不做验证，不显示警告

### 2025-11-23 11:25
- ✅ 创建 `system.py` - 系统基本信息（OS、Python环境、路径）
- ✅ 创建 `system_settings.py` - 系统设置检测（HDR、夜间模式、分辨率）
- 特点：system_settings 会进行验证并给出警告/错误

### 2025-11-23 11:30
- ✅ 创建 `python_environment.py` - Python 环境完整检测
- 功能：
  - Python 版本检测
  - 包管理器类型识别（pip/conda/uv/poetry/pipenv）
  - 虚拟环境检测（支持任意命名）
  - 依赖完整性检查（缺失包、版本不匹配）

### 2025-11-23 11:35
- ✅ 更新 `DiagnosticSuite` - 集成新检测器
- 新的检测顺序：
  1. hardware_info (硬件信息)
  2. system_info_new (系统信息)
  3. system_settings (系统设置)
  4. network_connectivity (网络连通性)
  5. python_environment (Python环境)
  6. environment_dependencies (组件依赖)
  7. path_validation (路径规范)
  8. system_info (旧版，向后兼容)
- 保持向后兼容性

### 2025-11-23 11:40
- ✅ 测试新检测器 - 运行成功
- 新检测器正常工作，python_environment 正确检测虚拟环境
- **阶段 1 完成** ✅

---

## 阶段 1 总结

已完成：
- ✅ 创建 3 个新检测器（hardware, system, system_settings）
- ✅ 创建 python_environment 检测器（包管理器识别、依赖检查）
- ✅ 集成到 DiagnosticSuite
- ✅ 测试通过

下一步：阶段 2 - 优化系统信息展示

---

## 注意事项

1. **向后兼容**: 保持现有 API 不变，避免破坏性更改
2. **渐进式重构**: 每个阶段独立提交，便于回滚
3. **测试覆盖**: 每个新功能都要有对应测试
4. **文档同步**: 代码变更后立即更新文档
