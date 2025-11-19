# OOPS 开发者入门指南

## 🚀 快速开始

### 环境准备
```bash
# 1. 克隆项目
git clone https://github.com/your-username/OOPS.git
cd OOPS

# 2. 创建虚拟环境（推荐使用conda或venv）
python -m venv .venv

# 3. 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 4. 安装开发依赖
pip install -r requirements-dev.txt
pip install -e .
```

### 项目结构概览
```
OOPS/
├── oops/                          # 核心Python包
│   ├── core/                      # 核心框架
│   ├── detectors/                 # 检测器模块
│   ├── knowledge/                 # 知识库系统
│   ├── reporters/                 # 报告生成器
│   ├── utils/                     # 工具函数
│   └── plugins/                   # 插件系统
├── configs/                       # 配置文件目录
├── tests/                         # 测试代码
├── docs/                          # 文档
└── scripts/                       # 构建和部署脚本
```

## 🛠️ 开发工作流

### 1. 代码规范
```bash
# 代码格式化
black oops/
isort oops/

# 代码检查
flake8 oops/
mypy oops/

# 运行测试
pytest tests/
```

### 2. 提交规范
```bash
# 使用pre-commit钩子
pre-commit install

# 提交前会自动运行：
# - black (代码格式化)
# - isort (导入排序)
# - flake8 (代码检查)
```

## 🔧 核心开发概念

### 检测器 (Detectors)
检测器是OOPS的核心组件，负责执行具体的检测任务。

#### 创建新的检测器
```python
# oops/detectors/my_detector.py
from .base_detector import BaseDetector

class MyDetector(BaseDetector):
    """自定义检测器示例"""
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "My Custom Detector"
    
    async def detect_async(self):
        """异步检测方法"""
        results = []
        
        # 执行检测逻辑
        for check in self.config.get('checks', []):
            result = await self._perform_check(check)
            results.append(result)
        
        return {
            'detector_name': self.name,
            'results': results,
            'summary': self._generate_summary(results)
        }
    
    def detect(self):
        """同步检测方法"""
        # 同步检测实现
        pass
```

#### 注册检测器
在 `oops/detectors/__init__.py` 中注册新的检测器：
```python
from .my_detector import MyDetector

__all__ = [
    # ... 其他检测器
    'MyDetector',
]
```

### 配置系统
OOPS使用分层配置系统，支持项目级覆盖和检测配置文件。

#### 配置结构
```yaml
# projects/zenless_zone_zero.yaml
project:
  id: "zenless_zone_zero"
  name: "绝区零一条龙"
  type: "game_script"

checks:
  my_custom_check:
    enabled: true
    config:
      check_param: "value"
      timeout: 30
```

#### 使用配置管理器
```python
from oops.core import AdvancedConfigManager

# 加载配置
config_manager = AdvancedConfigManager("oops_master.yaml")

# 获取项目配置
project_config = config_manager.get_project_config("zenless_zone_zero")

# 设置检测配置文件
config_manager.set_active_profile("full_scan")
```

## 📝 添加新项目支持

### 1. 创建项目配置模板
```bash
# 使用命令行工具创建新项目模板
python oops.py --create-project my_new_game --name "我的新游戏" --type game_script
```

### 2. 编辑项目配置
```yaml
# projects/my_new_game.yaml
project:
  id: "my_new_game"
  name: "我的新游戏"
  type: "game_script"
  description: "新游戏的自动化脚本"
  repository: "https://github.com/owner/my_new_game"

paths:
  install_path: "D:/MyNewGame"
  config_dir: "config"
  requirements_file: "requirements.txt"

checks:
  network:
    enabled: true
    config:
      git_repos:
        - url: "https://github.com/owner/my_new_game.git"
          required: true
      pypi_sources:
        - name: "官方源"
          url: "https://pypi.org/simple/"
      project_urls:
        - "https://mynewgame.com"

  # 添加其他检测模块...
```

### 3. 在主配置中启用项目
```yaml
# oops_master.yaml
projects:
  my_new_game:
    enabled: true
    config: "projects/my_new_game.yaml"
    overrides:
      enabled_checks:
        game_settings: true
```

## 🎮 游戏设置检测开发

### YAML配置定义
```yaml
game_settings:
  enabled: true
  config:
    navigation_steps:
      - name: "打开设置菜单"
        action: "click"
        target:
          type: "icon"           # 图标识别
          description: "设置图标"
          fallback:              # 回退机制
            type: "coordinate"   # 坐标点击
            x: 100
            y: 200
        timeout: 10
        retry: 3

    settings_to_check:
      - name: "分辨率"
        type: "text_detection"
        location: [100, 200, 300, 50]  # [x, y, width, height]
        expected_values: ["1920x1080", "2560x1440"]
        recommended: "1920x1080"
        validation:
          type: "exact_match"
          case_sensitive: false
```

### 检测器实现
```python
# oops/plugins/game_setting_detector/game_setting_detector.py
class GameSettingDetector:
    def __init__(self, config):
        self.config = config
        self.detection_strategy = self._create_detection_strategy()
    
    def _create_detection_strategy(self):
        """创建检测策略（YOLO -> 图像识别 -> 坐标回退）"""
        strategies = []
        
        # 1. YOLO检测
        if self._has_yolo_model():
            strategies.append(YOLODetectionStrategy())
        
        # 2. 图像识别
        strategies.append(ImageRecognitionStrategy())
        
        # 3. 坐标回退
        strategies.append(CoordinateFallbackStrategy())
        
        return FallbackStrategyChain(strategies)
    
    async def detect_setting(self, setting_config):
        """检测单个设置项"""
        # 使用策略链进行检测
        result = await self.detection_strategy.detect(setting_config)
        
        # 验证结果
        validated_result = self._validate_result(result, setting_config)
        
        return validated_result
```

## 🔍 虚拟环境检测优化

### 支持多种虚拟环境
```python
# oops/detectors/virtualenv_detector.py
class VirtualEnvDetector:
    def detect_virtualenv(self, project_root):
        """检测虚拟环境（支持venv、virtualenv、conda）"""
        env_types = [
            VenvEnvironment(project_root),
            VirtualenvEnvironment(project_root), 
            CondaEnvironment(project_root),
            PipenvEnvironment(project_root)
        ]
        
        for env_type in env_types:
            if env_type.exists():
                return env_type.analyze()
        
        return None

class CondaEnvironment:
    """Conda环境检测"""
    def exists(self):
        return (self.project_root / "environment.yml").exists() or \
               (self.project_root / ".conda").exists()
    
    def analyze(self):
        # Conda特定分析逻辑
        return {
            'type': 'conda',
            'env_file': str(self.project_root / "environment.yml"),
            'active_env': self._get_conda_env(),
            'packages': self._get_conda_packages()
        }
```

## 🌐 网络组件统一管理

### Git检测器基类
```python
# oops/detectors/git_detector.py
class GitDetector(BaseDetector):
    """Git检测器基类"""
    
    def __init__(self, config):
        super().__init__(config)
        self.git_client = self._create_git_client()
    
    def _create_git_client(self):
        """创建Git客户端（支持pygit2、gitpython、命令行）"""
        clients = []
        
        # 尝试使用pygit2
        try:
            import pygit2
            clients.append(PyGit2Client())
        except ImportError:
            pass
        
        # 尝试使用gitpython  
        try:
            import git
            clients.append(GitPythonClient())
        except ImportError:
            pass
        
        # 命令行回退
        clients.append(CommandLineGitClient())
        
        return FallbackClientChain(clients)
    
    async def check_repository(self, repo_config):
        """检查Git仓库"""
        return await self.git_client.check_repository(repo_config)
```

## 📊 测试开发

### 单元测试示例
```python
# tests/test_network_detector.py
import pytest
from oops.detectors.network_detector import NetworkDetector

class TestNetworkDetector:
    @pytest.fixture
    def detector(self):
        config = {
            'git_repos': [
                {'url': 'https://github.com/owner/repo.git', 'timeout': 30}
            ]
        }
        return NetworkDetector(config)
    
    @pytest.mark.asyncio
    async def test_git_repo_check(self, detector):
        """测试Git仓库检测"""
        result = await detector.detect_async()
        
        assert 'git_repos' in result
        assert len(result['git_repos']) > 0
        
    def test_config_validation(self, detector):
        """测试配置验证"""
        assert detector.validate_config() is True
```

### 集成测试
```python
# tests/integration/test_full_diagnostic.py
class TestFullDiagnostic:
    @pytest.mark.asyncio 
    async def test_zenless_zone_zero_diagnostic(self):
        """测试绝区零项目完整诊断"""
        suite = MultiProjectSuite()
        results = await suite.run_diagnostics(["zenless_zone_zero"])
        
        assert "zenless_zone_zero" in results
        assert results["zenless_zone_zero"]["status"] == "completed"
```

## 🚀 部署和打包

### 开发版本打包
```bash
# 构建开发版本
python setup.py sdist bdist_wheel

# 安装开发版本
pip install dist/oops-0.1.0-py3-none-any.whl
```

### 生产版本打包
```bash
# 使用PyInstaller打包为exe
pyinstaller oops.spec

# 生成的exe文件在 dist/ 目录
```

### 持续集成
GitHub Actions配置示例：
```yaml
# .github/workflows/test.yml
name: Test and Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
        
      - name: Run tests
        run: pytest tests/ --cov=oops --cov-report=xml
        
      - name: Code quality
        run: |
          black --check oops/
          isort --check-only oops/
          flake8 oops/
```

## 🔧 调试和故障排除

### 启用调试模式
```bash
# 启用详细日志
oops --project zenless_zone_zero --verbose

# 启用调试模式
export OOPS_DEBUG=1
python oops.py --project zenless_zone_zero
```

### 常见问题解决
1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   python -m venv .venv --clear
   ```

2. **依赖冲突**
   ```bash
   # 清理并重新安装
   pip freeze | xargs pip uninstall -y
   pip install -r requirements-dev.txt
   ```

3. **配置问题**
   ```bash
   # 验证配置
   python -c "from oops.core import AdvancedConfigManager; cm = AdvancedConfigManager(); print(cm.get_enabled_projects())"
   ```

## 📚 进一步学习

### 核心文档
- [`project_structure.md`](project_structure.md) - 项目架构和文件结构
- [`functional_design.md`](functional_design.md) - 功能模块详细设计
- [`multi_project_architecture.md`](multi_project_architecture.md) - 多项目支持架构
- [`game_setting_detection.md`](game_setting_detection.md) - 游戏设置检测实现

### API参考
- 核心框架: `oops.core` 模块
- 检测器: `oops.detectors` 模块  
- 配置管理: `oops.core.config_manager` 模块
- 报告生成: `oops.reporters` 模块

### 示例项目
查看 `examples/` 目录中的示例项目，了解实际使用方式。

---

**开始贡献吧！** 🎉

如果有任何问题，请查看 [Issues](https://github.com/your-username/OOPS/issues) 或加入我们的讨论。