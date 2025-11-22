# OOPS 开发者文档

**OOPS - One-click Operating Pre-check System (一键运行预检系统)**

> 让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly

---

## 🛠️ 开发环境设置

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

---

## 📚 核心文档索引

### 架构设计
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构设计
- **[project_structure.md](project_structure.md)** - 项目结构详解
- **[multi_project_architecture.md](multi_project_architecture.md)** - 多项目架构

### 功能文档
- **[FEATURE_LIST.md](FEATURE_LIST.md)** - 完整功能列表
- **[game_setting_yolo_fallback.md](game_setting_yolo_fallback.md)** - 游戏设置检测
- **[game_setting_yaml_template.md](game_setting_yaml_template.md)** - 配置模板

### 开发指南
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - 开发者指南
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - 文档导航
- **[report_design.md](report_design.md)** - 报告设计

### 技术文档
- **[ssl_certificate_repair.md](ssl_certificate_repair.md)** - SSL证书修复
- **[unified_git_detection.md](unified_git_detection.md)** - Git检测
- **[virtualenv_detection.md](virtualenv_detection.md)** - 虚拟环境检测

---

## 🏗️ 项目结构

```
OOPS/
├── oops/                       # 核心代码
│   ├── core/                   # 核心模块
│   │   ├── config.py          # 配置管理
│   │   ├── diagnostics.py     # 诊断引擎
│   │   ├── report.py          # 报告生成
│   │   └── project_detector.py # 项目检测
│   ├── detectors/             # 检测器
│   │   ├── network.py         # 网络检测
│   │   ├── environment.py     # 环境检测
│   │   ├── paths.py           # 路径检测
│   │   └── system_info.py     # 系统信息
│   ├── validators/            # 验证器
│   │   └── path_validator.py # 路径验证
│   └── knowledge/             # 知识库
│       └── issue_matcher.py   # 问题匹配
├── configs/                   # 配置文件
│   ├── oops_master.yaml      # 主配置
│   └── zenless_zone_zero.yaml # 项目配置
├── tests/                     # 测试代码
├── docs/                      # 文档
│   ├── dev/                   # 开发者文档
│   └── knowledge_base/        # 知识库
├── build/                     # 构建脚本
│   ├── scripts/              # 构建脚本
│   ├── docs/                 # 构建文档
│   └── config/               # 构建配置
└── reports/                   # 报告输出
```

---

## 🔧 添加新项目配置

### 1. 创建配置文件
```bash
# 使用命令创建
python oops.py --create-config my_project

# 或手动创建
cp configs/zenless_zone_zero.yaml configs/my_project.yaml
```

### 2. 编辑配置文件
```yaml
# configs/my_project.yaml
project:
  name: '我的项目'
  type: 'game_script'
  description: '项目描述'
  
checks:
  system_info:
    enabled: true
  network:
    enabled: true
    git_repos:
      - 'https://github.com/user/repo.git'
  environment:
    enabled: true
    python_version: '>=3.8'
  paths:
    enabled: true
```

### 3. 在主配置中启用
```yaml
# configs/oops_master.yaml
projects:
  my_project:
    enabled: true
    config: 'configs/my_project.yaml'
```

---

## 🧪 开发模块

### 检测模块开发
```python
from oops.core import DiagnosticSuite

# 创建检测套件
diagnostics = DiagnosticSuite(project="my_project")

# 运行检测
results = diagnostics.run_diagnostics()

# 生成报告
report = diagnostics.generate_report()
diagnostics.save_report("diagnostic_report.html")
```

### 自定义检测器
```python
from oops.core.config import DetectionRule

class MyDetector(DetectionRule):
    def __init__(self):
        self.name = "my_detector"
        self.description = "我的检测器"
    
    def check(self, config):
        # 检测逻辑
        return {
            'status': 'success',
            'message': '检测完成',
            'details': {}
        }
    
    def get_fix_suggestion(self, result):
        # 修复建议
        return "修复建议"
```

---

## 📦 构建和发布

### 构建可执行文件
```bash
# Windows
cd build/scripts
./build.bat

# Linux/macOS
cd build/scripts
./build.sh
```

### 发布检查清单
参见 [build/docs/RELEASE_CHECKLIST.md](../../build/docs/RELEASE_CHECKLIST.md)

---

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_config.py

# 生成覆盖率报告
pytest --cov=oops tests/
```

### 测试覆盖
- 配置管理测试
- 检测器单元测试
- 集成测试
- 报告生成测试

---

## 🎨 代码规范

### Python代码风格
- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 保持函数简洁

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 🤝 贡献指南

### 贡献流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码审查
- 确保所有测试通过
- 更新相关文档
- 遵循代码规范
- 添加必要的注释

---

## 📊 性能优化

### 检测性能
- 并发检测支持
- 超时控制
- 缓存机制
- 增量检测

### 报告生成
- 模块化生成
- 延迟加载
- 压缩优化
- 缓存复用

---

## 🐛 调试技巧

### 启用详细日志
```bash
python oops.py --verbose
```

### 查看日志文件
```bash
# Windows
type oops.log

# Linux/macOS
cat oops.log
```

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📝 文档维护

### 文档更新
- 保持文档与代码同步
- 更新示例代码
- 添加新功能说明
- 修正错误信息

### 文档结构
- 用户文档：主目录
- 开发者文档：docs/dev/
- 技术文档：docs/
- API文档：自动生成

---

## 🔗 相关链接

- **用户文档**: [README.md](../../README.md)
- **快速开始**: [QUICKSTART.md](../../QUICKSTART.md)
- **用户指南**: [USER_GUIDE.md](../../USER_GUIDE.md)
- **更新日志**: [CHANGELOG.md](../../CHANGELOG.md)
- **路线图**: [ROADMAP.md](../../ROADMAP.md)

---

**Happy Coding! 🚀**
