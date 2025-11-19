# OOPS 项目结构规划

## 整体目录结构

```
OOPS/
├── oops/                          # 核心 Python 包
│   ├── __init__.py               # 包初始化文件
│   ├── core/                     # 核心框架
│   │   ├── __init__.py
│   │   ├── diagnostic_suite.py   # 诊断套件主类
│   │   ├── config_manager.py     # 配置管理器
│   │   └── plugin_manager.py     # 插件管理器
│   ├── detectors/                # 检测器模块
│   │   ├── __init__.py
│   │   ├── base_detector.py      # 检测器基类
│   │   ├── network_detector.py   # 网络连通性检测
│   │   ├── environment_detector.py # 环境依赖检测
│   │   ├── path_detector.py      # 路径规范检测
│   │   ├── registry_detector.py  # 注册表检测
│   │   ├── hardware_detector.py  # 硬件健康检测
│   │   └── script_detector.py    # 脚本配置检测
│   ├── knowledge/                # 知识库系统
│   │   ├── __init__.py
│   │   ├── problem_kb.py         # 问题知识库
│   │   ├── solution_kb.py        # 解决方案库
│   │   └── historical_data/      # 历史数据
│   │       ├── __init__.py
│   │       ├── sample_parser.py  # sample.txt 解析器
│   │       └── connectivity_data.py # 连通性测试数据
│   ├── reporters/                # 报告生成器
│   │   ├── __init__.py
│   │   ├── base_reporter.py      # 报告器基类
│   │   ├── html_reporter.py      # HTML 报告生成
│   │   ├── json_reporter.py      # JSON 报告生成
│   │   └── text_reporter.py      # 文本报告生成
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── network_utils.py      # 网络工具
│   │   ├── system_utils.py       # 系统工具
│   │   ├── file_utils.py         # 文件工具
│   │   └── logging_utils.py      # 日志工具
│   └── plugins/                  # 插件系统
│       ├── __init__.py
│       ├── base_plugin.py        # 插件基类
│       ├── yolo_adapter/         # YOLO 项目适配器
│       │   ├── __init__.py
│       │   ├── yolo_detector.py  # YOLO 专用检测器
│       │   └── yolo_configs.py   # YOLO 配置模板
│       └── game_scripts/         # 游戏脚本适配器
│           ├── __init__.py
│           ├── game_detector.py  # 游戏脚本检测器
│           └── game_configs.py   # 游戏配置模板
├── configs/                      # 配置文件目录
│   ├── default.yaml              # 默认配置
│   ├── yolo_project.yaml         # YOLO 项目配置模板
│   ├── game_script.yaml          # 游戏脚本配置模板
│   └── custom/                   # 用户自定义配置
│       └── README.md
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_core/                # 核心模块测试
│   ├── test_detectors/           # 检测器测试
│   ├── test_knowledge/           # 知识库测试
│   ├── test_reporters/           # 报告器测试
│   ├── test_utils/               # 工具函数测试
│   └── fixtures/                 # 测试数据
├── docs/                         # 文档目录
│   ├── index.md                  # 文档首页
│   ├── user_guide/               # 用户指南
│   ├── developer_guide/          # 开发者指南
│   ├── api_reference/            # API 参考
│   └── examples/                 # 使用示例
├── scripts/                      # 脚本目录
│   ├── install.py                # 安装脚本
│   ├── update_kb.py              # 知识库更新脚本
│   └── benchmark.py              # 性能测试脚本
├── examples/                     # 示例项目
│   ├── basic_usage/              # 基础使用示例
│   ├── yolo_project/             # YOLO 项目示例
│   └── game_script/              # 游戏脚本示例
├── data/                         # 数据目录
│   ├── historical/               # 历史问题数据
│   │   ├── sample.txt            # 客服问题总结
│   │   └── connectivity_reports/ # 连通性测试报告
│   ├── templates/                # 报告模板
│   │   ├── html_report.html      # HTML 报告模板
│   │   └── text_report.txt       # 文本报告模板
│   └── cache/                    # 缓存数据
├── .github/                      # GitHub 配置
│   ├── workflows/                # CI/CD 工作流
│   │   ├── test.yml              # 测试工作流
│   │   └── release.yml           # 发布工作流
│   └── ISSUE_TEMPLATE/           # Issue 模板
├── requirements.txt              # 生产环境依赖
├── requirements-dev.txt          # 开发环境依赖
├── setup.py                      # 包安装配置
├── pyproject.toml                # 项目配置
├── oops.py                       # 命令行入口点
├── README.md                     # 项目说明
├── CONTRIBUTING.md               # 贡献指南
├── LICENSE                       # 许可证文件
└── .gitignore                    # Git 忽略文件
```

## 核心文件说明

### 主要入口文件

#### `oops.py` - 命令行入口点
```python
#!/usr/bin/env python3
"""
OOPS 命令行入口点
Open-source One-click Problem Solver
"""

import argparse
import sys
from oops.core import DiagnosticSuite

def main():
    parser = argparse.ArgumentParser(description='OOPS - 开源一键问题排查器')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--project-type', '-t', choices=['yolo', 'game', 'custom'], 
                       help='项目类型')
    parser.add_argument('--output', '-o', help='输出目录')
    parser.add_argument('--format', '-f', choices=['html', 'json', 'text'], 
                       default='html', help='报告格式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 创建诊断套件并运行
    suite = DiagnosticSuite(config_path=args.config, project_type=args.project_type)
    suite.run_diagnostics()
    suite.generate_report(format=args.format, output_dir=args.output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

#### `setup.py` - 包安装配置
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="oops-tool",
    version="0.1.0",
    author="OOPS Team",
    author_email="oops@example.com",
    description="Open-source One-click Problem Solver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/OOPS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "oops=oops.cli:main",
        ],
    },
)
```

### 配置文件示例

#### `configs/default.yaml`
```yaml
# OOPS 默认配置
project:
  name: "Default Project"
  type: "generic"
  version: "1.0.0"

network:
  git_repos:
    - url: "https://github.com/example/main.git"
      timeout: 30
      required: true
  pypi_sources:
    - name: "官方 PyPI"
      url: "https://pypi.org/simple/"
      timeout: 10
    - name: "清华镜像"
      url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
      timeout: 10
  project_urls:
    - "https://example.com"
    - "https://docs.example.com"

environment:
  python:
    min_version: "3.8"
    max_version: "3.11"
  required_packages:
    - "requests>=2.25.0"
    - "pyyaml>=5.4.0"
  system_requirements:
    - "vc_redist>=2015"

paths:
  check_chinese: true
  check_permissions: true
  max_path_length: 260
  forbidden_chars: [" ", "*", "?", "<", ">", "|"]

registry:
  checks: []

hardware:
  min_ram_gb: 4
  min_disk_gb: 1
  check_gpu: false

report:
  format: "html"
  output_dir: "./oops_reports"
  include_solutions: true
  severity_levels: ["critical", "high", "medium", "low"]
```

#### `configs/yolo_project.yaml`
```yaml
# YOLO 项目专用配置
project:
  name: "YOLO Project"
  type: "yolo_python"
  version: "1.0.0"

network:
  git_repos:
    - url: "https://github.com/ultralytics/yolov5.git"
      timeout: 30
      required: true
  pypi_sources:
    - name: "官方源"
      url: "https://pypi.org/simple/"
    - name: "清华源"
      url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
  project_urls:
    - "https://ultralytics.com/"
    - "https://docs.ultralytics.com/"

environment:
  python:
    min_version: "3.8"
    max_version: "3.11"
  required_packages:
    - "torch>=1.7.0"
    - "torchvision>=0.8.0"
    - "opencv-python>=4.1.0"
    - "numpy>=1.17.0"
    - "pillow>=7.1.0"
  system_requirements:
    - "cuda>=10.2"
    - "cudnn>=8.0"

paths:
  check_chinese: true
  check_permissions: true
  required_dirs:
    - "models/"
    - "data/"
    - "utils/"

hardware:
  min_ram_gb: 8
  min_disk_gb: 10
  check_gpu: true
  recommended_gpu: "NVIDIA GPU with CUDA support"

yolo_specific:
  model_formats: [".pt", ".onnx", ".engine"]
  data_yaml_required: true
  weights_download: true
```

### 核心类文件结构

#### `oops/core/diagnostic_suite.py`
```python
"""
诊断套件主类
负责协调所有检测器和生成报告
"""

import asyncio
import logging
from typing import List, Dict, Any
from pathlib import Path

from ..detectors import (
    NetworkDetector, 
    EnvironmentDetector,
    PathDetector,
    HardwareDetector
)
from ..reporters import ReportGenerator
from .config_manager import ConfigManager

class DiagnosticSuite:
    """诊断套件主类"""
    
    def __init__(self, config_path: str = None, project_type: str = None):
        self.config_manager = ConfigManager(config_path, project_type)
        self.config = self.config_manager.load_config()
        self.detectors = self._initialize_detectors()
        self.results = {}
        self.logger = logging.getLogger(__name__)
    
    def _initialize_detectors(self) -> List:
        """初始化检测器"""
        detectors = [
            NetworkDetector(self.config),
            EnvironmentDetector(self.config),
            PathDetector(self.config),
            HardwareDetector(self.config)
        ]
        
        # 根据项目类型添加专用检测器
        if self.config['project']['type'] == 'yolo_python':
            from ..plugins.yolo_adapter import YOLODetector
            detectors.append(YOLODetector(self.config))
        
        return detectors
    
    async def run_diagnostics_async(self):
        """异步运行所有诊断"""
        tasks = [detector.detect_async() for detector in self.detectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for detector, result in zip(self.detectors, results):
            self.results[detector.__class__.__name__] = result
        
        return self.results
    
    def run_diagnostics(self):
        """同步运行所有诊断"""
        for detector in self.detectors:
            try:
                self.logger.info(f"运行检测器: {detector.__class__.__name__}")
                result = detector.detect()
                self.results[detector.__class__.__name__] = result
            except Exception as e:
                self.logger.error(f"检测器 {detector.__class__.__name__} 执行失败: {e}")
                self.results[detector.__class__.__name__] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return self.results
    
    def generate_report(self, format: str = 'html', output_dir: str = None):
        """生成检测报告"""
        reporter = ReportGenerator(format=format)
        report_content = reporter.generate_report(self.results)
        
        if output_dir:
            output_path = Path(output_dir) / f"oops_report.{format}"
            reporter.save_report(report_content, output_path)
            return output_path
        
        return report_content
    
    def get_summary(self) -> Dict[str, Any]:
        """获取检测摘要"""
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warnings = 0
        
        for detector_name, result in self.results.items():
            if 'checks' in result:
                for check in result['checks']:
                    total_checks += 1
                    if check['status'] == 'passed':
                        passed_checks += 1
                    elif check['status'] == 'failed':
                        failed_checks += 1
                    elif check['status'] == 'warning':
                        warnings += 1
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'warning_checks': warnings,
            'success_rate': passed_checks / total_checks if total_checks > 0 else 0
        }
```

## 开发环境设置

### 依赖管理

#### `requirements.txt`
```
# 核心依赖
pyyaml>=6.0
requests>=2.28.0
aiohttp>=3.8.0
jinja2>=3.1.0
psutil>=5.9.0
colorama>=0.4.0
```

#### `requirements-dev.txt`
```
# 开发依赖
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

### 开发工具配置

#### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203,W503"]
```

## 部署说明

### 开发模式安装
```bash
git clone https://github.com/your-username/OOPS.git
cd OOPS
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements-dev.txt
pip install -e .
```

### 生产环境安装
```bash
pip install oops-tool
```

### Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install .

CMD ["oops", "--help"]
```

这个项目结构规划提供了完整的开发框架，支持模块化扩展和插件系统，能够满足开源脚本自检的各种需求。