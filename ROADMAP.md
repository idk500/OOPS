# OOPS 项目路线图 (Roadmap)

## 📋 三步走战略

### 🎯 总体目标
1. **Phase 1**: 配置文件 → 执行器 → 报告（基础诊断系统）
2. **Phase 2**: 嗅探器 → 配置文件 → 执行器 → 报告（智能配置生成）
3. **Phase 3**: 嗅探器 → 配置文件 → 执行器 → 报告 → 自动修复（完整闭环）

---

## 🚀 Phase 1: 基础诊断系统 (v1.0) - 当前阶段

### 目标
建立稳定的"配置 → 执行 → 报告"流程，完成核心检测功能。

### ✅ 已完成任务
- [x] 项目架构设计
- [x] 配置管理系统（ConfigManager）
- [x] 诊断执行器（DiagnosticSuite）
- [x] 报告生成器（ReportGenerator - HTML/JSON/Markdown）
- [x] 网络连通性检测器
- [x] 环境依赖检测器
- [x] 路径规范检测器
- [x] 自动运行体验优化
- [x] DirectX检测修复（无弹窗）
- [x] 自动打开浏览器报告

### 🔄 进行中任务

#### 1.1 策略转化验证 (优先级: 高)
**任务**: 确保 `docs/deprecated/ref` 中的所有策略已转化到代码

**检查清单**:
- [ ] `connectivity_test.py` 策略转化
  - [x] PyPI源检测 → 已实现
  - [x] Git仓库检测 → 已实现
  - [x] HTTP兜底方案 → 已实现
  - [ ] 米哈游API检测 → 待添加
  - [ ] 公告系统检测 → 待添加
  - [ ] GitHub代理检测 → 待添加

- [ ] `debug.bat` 策略转化
  - [ ] SSL证书修复 → 待实现
  - [ ] Git安全目录配置 → 待实现
  - [ ] 虚拟环境重建 → 待实现
  - [ ] PowerShell路径检查 → 待实现
  - [ ] 依赖包重装 → 待实现

- [x] `sample.txt` 知识库转化
  - [x] 已转化到 `docs/knowledge_base/zenless_zone_zero_knowledge.md`
  - [x] 常见问题已整理
  - [x] 硬件配置要求已记录

**实施步骤**:
```bash
# 1. 添加米哈游API检测
# 文件: oops/detectors/network.py
# 新增方法: _check_mihoyo_api()

# 2. 实现SSL证书修复
# 文件: oops/detectors/ssl_repair.py (新建)
# 参考: docs/deprecated/ref/debug.bat

# 3. 实现Git安全目录配置
# 文件: oops/detectors/git_config.py (新建)
```

#### 1.2 项目清理和归档 (优先级: 高)
**任务**: 清理冗余文档和代码，准备打基线

**清理清单**:
- [ ] 归档过时文档
  ```
  docs/deprecated/
  ├── dev.md → 已过时，保留归档
  ├── functional_design.md → 已过时，保留归档
  ├── game_setting_detection.md → 已过时，保留归档
  └── ref/
      ├── connectivity_test.py → 策略已转化，保留参考
      ├── connectivity_test.exe → 删除
      ├── 网络诊断.exe → 删除
      ├── debug.bat → 策略转化中，保留参考
      ├── sample.txt → 已转化，保留参考
      └── connectivity_test_report.json → 保留参考
  ```

- [ ] 删除冗余代码
  ```
  # 检查是否有未使用的导入
  # 检查是否有重复的函数
  # 检查是否有过时的测试代码
  ```

- [ ] 统一文档结构
  ```
  docs/
  ├── dev/ (开发文档 - 保留)
  ├── knowledge_base/ (知识库 - 保留)
  └── deprecated/ (归档文档 - 整理)
  ```

#### 1.3 测试覆盖完善 (优先级: 中)
**任务**: 补充核心模块的单元测试

**测试清单**:
- [x] `tests/test_config.py` - 配置管理测试
- [ ] `tests/test_diagnostics.py` - 诊断执行器测试
- [ ] `tests/test_network.py` - 网络检测器测试
- [ ] `tests/test_environment.py` - 环境检测器测试
- [ ] `tests/test_paths.py` - 路径检测器测试
- [ ] `tests/test_report.py` - 报告生成器测试

**目标覆盖率**: 80%+

#### 1.4 基线准备 (优先级: 高)
**任务**: 准备 v1.0 基线发布

**检查清单**:
- [ ] 所有核心功能测试通过
- [ ] 文档完整且最新
- [ ] 无已知严重bug
- [ ] 性能测试通过
- [ ] 创建 CHANGELOG.md
- [ ] 创建 LICENSE 文件
- [ ] 更新版本号到 1.0.0

---

## 🔍 Phase 2: 智能配置生成 (v2.0) - 规划阶段

### 目标
实现"嗅探器"功能，自动检测系统环境并生成配置文件。

### 核心功能

#### 2.1 环境嗅探器 (Sniffer)
**功能**: 自动检测系统环境，生成项目配置

**检测项目**:
```yaml
system_detection:
  - 操作系统版本
  - Python安装路径和版本
  - 虚拟环境检测
  - Git客户端检测
  - 系统运行库检测
  - 网络环境检测
  
project_detection:
  - 扫描常见安装路径
  - 识别项目类型
  - 检测配置文件
  - 分析依赖关系
```

**实施步骤**:
```python
# 1. 创建嗅探器基类
# 文件: oops/core/sniffer.py
class SystemSniffer:
    def detect_os(self)
    def detect_python(self)
    def detect_git(self)
    def detect_network(self)

# 2. 创建项目嗅探器
# 文件: oops/sniffers/project_sniffer.py
class ProjectSniffer:
    def scan_directories(self)
    def identify_project_type(self)
    def detect_config_files(self)

# 3. 配置生成器
# 文件: oops/core/config_generator.py
class ConfigGenerator:
    def generate_from_detection(self)
    def validate_generated_config(self)
```

#### 2.2 智能配置生成
**功能**: 根据嗅探结果自动生成配置文件

**生成流程**:
```
1. 运行系统嗅探 → 获取系统信息
2. 运行项目嗅探 → 识别项目类型
3. 匹配配置模板 → 选择合适模板
4. 填充配置参数 → 生成配置文件
5. 验证配置有效性 → 确保可用
6. 保存配置文件 → 写入磁盘
```

**命令示例**:
```bash
# 自动检测并生成配置
python oops.py --auto-detect

# 指定项目类型生成配置
python oops.py --generate-config --type game_script

# 扫描目录并生成配置
python oops.py --scan-dir "D:/ZZZ-OD" --generate-config
```

#### 2.3 配置推荐系统
**功能**: 基于检测结果提供配置建议

**推荐内容**:
- 最佳PyPI源选择
- 网络代理配置建议
- 虚拟环境配置建议
- 路径优化建议

---

## 🛠️ Phase 3: 自动修复系统 (v3.0) - 未来规划

### 目标
实现完整的"检测 → 诊断 → 修复"闭环。

### 核心功能

#### 3.1 自动修复引擎
**功能**: 根据检测结果自动修复问题

**修复能力**:
```yaml
network_fixes:
  - SSL证书修复
  - Git配置修复
  - 代理配置修复
  - DNS配置修复

environment_fixes:
  - 虚拟环境重建
  - 依赖包重装
  - 系统库安装
  - 环境变量配置

path_fixes:
  - 路径权限修复
  - 符号链接处理
  - 路径迁移建议
```

**实施步骤**:
```python
# 1. 创建修复器基类
# 文件: oops/core/fixer.py
class AutoFixer:
    def can_fix(self, issue)
    def fix(self, issue)
    def verify_fix(self, issue)

# 2. 创建具体修复器
# 文件: oops/fixers/
- ssl_fixer.py
- git_fixer.py
- venv_fixer.py
- path_fixer.py

# 3. 修复流程管理
# 文件: oops/core/fix_manager.py
class FixManager:
    def plan_fixes(self, issues)
    def execute_fixes(self, plan)
    def rollback_if_failed(self, fix)
```

#### 3.2 安全修复机制
**功能**: 确保修复操作的安全性

**安全措施**:
- 修复前备份
- 用户确认机制
- 回滚功能
- 修复日志记录

**命令示例**:
```bash
# 自动修复（需要确认）
python oops.py --auto-fix

# 自动修复（无需确认，危险）
python oops.py --auto-fix --yes

# 仅显示修复计划
python oops.py --plan-fix

# 回滚上次修复
python oops.py --rollback
```

#### 3.3 修复知识库
**功能**: 基于历史问题建立修复知识库

**知识库内容**:
- 常见问题修复方案
- 修复成功率统计
- 用户反馈收集
- 修复方案优化

---

## 📊 里程碑时间表

### Phase 1: 基础诊断系统 (v1.0)
- **开始时间**: 2024-11-01
- **目标完成**: 2024-12-01
- **当前进度**: 85%

**关键节点**:
- [x] 2024-11-15: 核心框架完成
- [x] 2024-11-21: 用户体验优化完成
- [ ] 2024-11-25: 策略转化完成
- [ ] 2024-11-28: 测试覆盖完成
- [ ] 2024-12-01: v1.0 基线发布

### Phase 2: 智能配置生成 (v2.0)
- **开始时间**: 2024-12-01
- **目标完成**: 2025-01-31
- **当前进度**: 0%

**关键节点**:
- [ ] 2024-12-15: 嗅探器框架完成
- [ ] 2024-12-31: 配置生成器完成
- [ ] 2025-01-15: 推荐系统完成
- [ ] 2025-01-31: v2.0 发布

### Phase 3: 自动修复系统 (v3.0)
- **开始时间**: 2025-02-01
- **目标完成**: 2025-03-31
- **当前进度**: 0%

**关键节点**:
- [ ] 2025-02-15: 修复引擎框架完成
- [ ] 2025-02-28: 基础修复器完成
- [ ] 2025-03-15: 安全机制完成
- [ ] 2025-03-31: v3.0 发布

---

## 🎯 当前优先级任务清单

### 本周任务 (Week 1)
1. **策略转化验证** (2天)
   - [ ] 添加米哈游API检测
   - [ ] 添加GitHub代理检测
   - [ ] 实现SSL证书检测

2. **项目清理** (1天)
   - [ ] 删除.exe文件
   - [ ] 整理deprecated目录
   - [ ] 统一文档结构

3. **测试补充** (2天)
   - [ ] 编写diagnostics测试
   - [ ] 编写network测试
   - [ ] 编写environment测试

### 下周任务 (Week 2)
1. **基线准备** (3天)
   - [ ] 创建CHANGELOG.md
   - [ ] 创建LICENSE
   - [ ] 更新所有文档
   - [ ] 版本号更新到1.0.0

2. **发布准备** (2天)
   - [ ] 打包测试
   - [ ] 性能测试
   - [ ] 用户验收测试

---

## 📝 技术债务清单

### 高优先级
- [ ] 添加类型注解（使用TypedDict或dataclass）
- [ ] 改进异常处理（区分异常类型）
- [ ] 添加配置缓存机制
- [ ] 实现日志轮转

### 中优先级
- [ ] 性能优化（连接池、超时控制）
- [ ] 添加进度条显示
- [ ] 使用pydantic验证配置
- [ ] 补充API文档

### 低优先级
- [ ] 代码复杂度优化
- [ ] 添加性能监控
- [ ] 国际化支持
- [ ] 插件系统设计

---

## 🤔 设计决策记录

### 为什么选择三步走？
1. **渐进式开发**: 避免一次性开发过多功能导致迷失
2. **快速迭代**: 每个阶段都有可交付的成果
3. **用户反馈**: 及时收集用户反馈，调整方向
4. **风险控制**: 降低技术风险，确保项目可控

### 为什么Phase 1不包含自动修复？
1. **复杂度控制**: 自动修复涉及系统修改，风险较高
2. **用户信任**: 需要先建立用户对诊断功能的信任
3. **数据积累**: 需要收集足够的问题数据才能设计好修复方案

### 为什么需要嗅探器？
1. **降低门槛**: 用户无需手动配置，提升易用性
2. **减少错误**: 自动检测减少配置错误
3. **智能推荐**: 基于实际环境提供最佳配置

---

## 📞 反馈和建议

如有任何建议或问题，请通过以下方式反馈：
- GitHub Issues: [项目地址]
- 邮件: oops@example.com
- 讨论区: [讨论地址]

---

**最后更新**: 2024-11-21
**维护者**: OOPS开发团队
