# 多项目支持架构优化设计

## 当前架构分析

### 现有问题
1. **配置分散**: 每个项目有自己的YAML配置，缺乏统一管理
2. **检测开关不灵活**: 无法在运行时动态启用/禁用特定检测
3. **项目间复用困难**: 相似项目的配置无法有效复用
4. **扩展性不足**: 新增项目需要手动创建完整配置

## 优化后的架构设计

### 1. 分层配置系统

#### 总配置文件 (`oops_master.yaml`)
```yaml
# 主配置文件 - 控制全局设置和项目启用状态
version: "2.0"
config_type: "master"

global:
  output_dir: "./oops_reports"
  default_report_format: "html"
  verbose: false
  max_concurrent_checks: 5
  timeout_multiplier: 1.0

  # 全局检测开关
  enabled_checks:
    network: true
    environment: true  
    paths: true
    virtualenv: true
    registry: false
    hardware: false
    game_settings: false  # 默认关闭，需要时开启

projects:
  # 项目配置引用
  zenless_zone_zero:
    enabled: true
    config: "projects/zenless_zone_zero.yaml"
    overrides:
      enabled_checks:
        game_settings: true  # 为这个项目启用游戏设置检测
      game_executable: "C:\\Program Files\\miHoYo Launcher\\games\\ZenlessZoneZero Game\\ZenlessZoneZero.exe"

  maa_assistant_arknights:
    enabled: true
    config: "projects/maa_assistant_arknights.yaml"
    overrides:
      enabled_checks:
        game_settings: true
      game_executable: "C:\\Program Files\\MaaAssistantArknights\\MaaAssistantArknights.exe"

  ok_wuthering_waves:
    enabled: false  # 暂时禁用
    config: "projects/ok_wuthering_waves.yaml"

  # 模板项目 - 用于快速创建新项目配置
  _template:
    enabled: false
    config: "projects/_template.yaml"

profiles:
  # 检测配置文件 - 定义不同检测场景
  quick_scan:
    description: "快速扫描 - 只检查关键项目"
    enabled_checks:
      network: true
      environment: true
      paths: true
      virtualenv: true
      game_settings: false
    timeout_multiplier: 0.5

  full_scan:
    description: "完整扫描 - 检查所有项目"
    enabled_checks:
      network: true
      environment: true
      paths: true
      virtualenv: true
      registry: true
      hardware: true
      game_settings: true
    timeout_multiplier: 1.0

  game_only:
    description: "仅游戏设置检测"
    enabled_checks:
      network: false
      environment: false
      paths: false
      virtualenv: false
      game_settings: true
    timeout_multiplier: 1.0
### 2. 项目配置文件结构

#### 项目基础配置 (`projects/_template.yaml`)
```yaml
# 项目配置模板
project:
  id: "_template"  # 项目唯一标识
  name: "项目名称"
  type: "game_script"  # game_script | yolo_project | generic
  description: "项目描述"
  repository: "https://github.com/owner/repo"
  
  # 项目特定路径
  paths:
    install_path: "D:/Projects/TemplateProject"  # 默认安装路径
    config_dir: "config"  # 配置文件目录
    models_dir: "assets/models"  # 模型文件目录
    requirements_file: "requirements.txt"  # 依赖文件

# 检测配置 - 每个检测模块都可以单独启用/禁用
checks:
  network:
    enabled: true
    description: "网络连通性检测"
    config:
      git_repos:
        - url: "https://github.com/owner/repo.git"
          required: true
          timeout: 30
      pypi_sources:
        - name: "官方源"
          url: "https://pypi.org/simple/"
        - name: "清华源"
          url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
      project_urls:
        - "https://project-homepage.com"

  environment:
    enabled: true
    description: "环境依赖检测"
    config:
      python:
        min_version: "3.8"
        max_version: "3.11"
      required_packages:
        - "opencv-python>=4.5.0"
        - "torch>=1.9.0"
      system_requirements:
        - "cuda>=11.1"

  paths:
    enabled: true
    description: "路径规范检测"
    config:
      check_chinese: true
      check_permissions: true
      max_path_length: 260

  virtualenv:
    enabled: true
    description: "虚拟环境检测"
    config:
      auto_detect: true
      common_paths: [".venv", "venv", "env"]
      validate_requirements: true

  game_settings:
    enabled: false  # 默认不启用游戏设置检测
    description: "游戏设置检测"
    config:
      executable: ""  # 由主配置覆盖
      navigation_steps: []
      settings_to_check: []
```

#### 具体项目配置示例

##### ZenlessZoneZero-OneDragon (`projects/zenless_zone_zero.yaml`)
```yaml
project:
  id: "zenless_zone_zero"
  name: "绝区零一条龙"
  type: "game_script"
  description: "绝区零自动化脚本"
  repository: "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon"
  
  paths:
    install_path: "D:/ZZZ-OD"
    config_dir: "config"
    models_dir: "assets/models"
    requirements_file: "requirements.txt"

checks:
  network:
    enabled: true
    config:
      git_repos:
        - url: "https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"
          required: true
        - url: "https://gitee.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git"
          required: false
      pypi_sources:
        - name: "官方源"
          url: "https://pypi.org/simple/"
        - name: "清华源"
          url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
        - name: "阿里云"
          url: "https://mirrors.aliyun.com/pypi/simple/"
      project_urls:
        - "https://one-dragon.com/zzz/zh/home.html"
        - "https://docs.qq.com/doc/p/7add96a4600d363b75d2df83bb2635a7c6a969b5"

  environment:
    enabled: true
    config:
      python:
        min_version: "3.8"
        max_version: "3.11"
      required_packages:
        - "opencv-python>=4.5.0"
        - "torch>=1.9.0"
        - "numpy>=1.21.0"
        - "pillow>=7.1.0"
      system_requirements:
        - "cuda>=10.2"
        - "cudnn>=8.0"

  game_settings:
    enabled: true
    config:
      navigation_steps:
        - name: "打开主菜单"
          action: "click"
          target:
            type: "icon"
            description: "主菜单按钮"
          timeout: 10
          retry: 3
        
        - name: "进入设置"
          action: "click"
          target:
            type: "text" 
            text: "设置"
          timeout: 5
          retry: 2

      settings_to_check:
        - name: "帧率设置"
          type: "text_detection"
          location: [100, 200, 200, 50]
          expected_values: ["30", "60"]
          recommended: "60"
        
        - name: "分辨率"
          type: "text_detection"
          location: [150, 250, 300, 50] 
          expected_values: ["1920x1080", "2560x1440"]
          recommended: "1920x1080"
```

##### MaaAssistantArknights (`projects/maa_assistant_arknights.yaml`)
```yaml
project:
  id: "maa_assistant_arknights"
  name: "MAA明日方舟助手"
  type: "game_script" 
  description: "明日方舟自动化助手"
  repository: "https://github.com/MaaAssistantArknights/MaaAssistantArknights"
  
  paths:
    install_path: "C:/Program Files/MaaAssistantArknights"
    config_dir: "config"
    models_dir: "assets/models"
    requirements_file: "requirements.txt"

checks:
  network:
    enabled: true
    config:
      git_repos:
        - url: "https://github.com/MaaAssistantArknights/MaaAssistantArknights.git"
          required: true
      pypi_sources:
        - name: "官方源"
          url: "https://pypi.org/simple/"
        - name: "清华源"
          url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
      project_urls:
        - "https://maa.plus/"
        - "https://docs.maa.plus/"

  environment:
    enabled: true
    config:
      python:
        min_version: "3.8"
        max_version: "3.11"
      required_packages:
        - "opencv-python>=4.5.0"
        - "onnxruntime>=1.8.0"
        - "pytest>=6.0.0"

  game_settings:
    enabled: true
    config:
      navigation_steps:
        - name: "打开设置菜单"
          action: "click"
          target:
            type: "icon"
            description: "设置图标"
          timeout: 10
          retry: 3

      settings_to_check:
        - name: "战斗速度"
          type: "text_detection"
          location: [120, 180, 180, 40]
          expected_values: ["1x", "2x"]
          recommended: "2x"
        
        - name: "自动战斗"
          type: "toggle_detection" 
          location: [140, 220, 160, 35]
          expected_values: ["开启", "关闭"]
          recommended: "开启"
```
### 3. 配置管理器优化

```python
# oops/core/advanced_config_manager.py
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class AdvancedConfigManager:
    """高级配置管理器 - 支持多项目和配置覆盖"""
    
    def __init__(self, master_config_path: str = "oops_master.yaml"):
        self.master_config_path = Path(master_config_path)
        self.master_config = self._load_master_config()
        self.projects_config = {}
        self.active_profile = self.master_config['global'].get('default_profile', 'quick_scan')
        self.logger = logging.getLogger(__name__)
        
        # 加载启用的项目配置
        self._load_project_configs()
    
    def _load_master_config(self) -> Dict:
        """加载主配置文件"""
        if not self.master_config_path.exists():
            raise FileNotFoundError(f"主配置文件不存在: {self.master_config_path}")
        
        with open(self.master_config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_project_configs(self):
        """加载所有启用的项目配置"""
        for project_id, project_info in self.master_config.get('projects', {}).items():
            if project_info.get('enabled', False):
                config_path = project_info['config']
                project_config = self._load_project_config(config_path)
                
                # 应用覆盖配置
                overrides = project_info.get('overrides', {})
                project_config = self._apply_overrides(project_config, overrides)
                
                # 应用当前检测配置文件
                profile_config = self.master_config['profiles'].get(self.active_profile, {})
                project_config = self._apply_profile(project_config, profile_config)
                
                self.projects_config[project_id] = project_config
    
    def _load_project_config(self, config_path: str) -> Dict:
        """加载单个项目配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"项目配置文件不存在: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _apply_overrides(self, project_config: Dict, overrides: Dict) -> Dict:
        """应用覆盖配置"""
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(project_config, overrides)
    
    def _apply_profile(self, project_config: Dict, profile_config: Dict) -> Dict:
        """应用检测配置文件"""
        # 覆盖检测模块的启用状态
        enabled_checks = profile_config.get('enabled_checks', {})
        for check_type, enabled in enabled_checks.items():
            if check_type in project_config.get('checks', {}):
                project_config['checks'][check_type]['enabled'] = enabled
        
        return project_config
    
    def set_active_profile(self, profile_name: str):
        """设置当前检测配置文件"""
        if profile_name not in self.master_config.get('profiles', {}):
            raise ValueError(f"未知的检测配置文件: {profile_name}")
        
        self.active_profile = profile_name
        self._load_project_configs()  # 重新加载配置以应用新的配置文件
    
    def get_enabled_projects(self) -> List[str]:
        """获取启用的项目列表"""
        return list(self.projects_config.keys())
    
    def get_project_config(self, project_id: str) -> Optional[Dict]:
        """获取项目配置"""
        return self.projects_config.get(project_id)
    
    def get_global_config(self) -> Dict:
        """获取全局配置"""
        return self.master_config.get('global', {})
    
    def get_profile_config(self, profile_name: str) -> Optional[Dict]:
        """获取检测配置文件"""
        return self.master_config['profiles'].get(profile_name)
    
    def create_project_template(self, project_id: str, project_info: Dict) -> str:
        """创建新项目配置模板"""
        template_path = Path("projects/_template.yaml")
        if not template_path.exists():
            raise FileNotFoundError("项目模板不存在")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        
        # 更新项目信息
        template['project'].update({
            'id': project_id,
            'name': project_info.get('name', project_id),
            'type': project_info.get('type', 'generic'),
            'description': project_info.get('description', ''),
            'repository': project_info.get('repository', '')
        })
        
        # 保存新项目配置
        new_config_path = Path(f"projects/{project_id}.yaml")
        with open(new_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, allow_unicode=True, indent=2)
        
        return str(new_config_path)
```
### 4. 多项目诊断套件

```python
# oops/core/multi_project_suite.py
import asyncio
import logging
from typing import Dict, List, Any
from pathlib import Path

from .advanced_config_manager import AdvancedConfigManager
from ..detectors import (
    NetworkDetector, 
    EnvironmentDetector,
    PathDetector, 
    VirtualEnvDetector
)
from ..plugins.game_setting_detector import GameSettingDetector

class MultiProjectSuite:
    """多项目诊断套件"""
    
    def __init__(self, config_manager: AdvancedConfigManager):
        self.config_manager = config_manager
        self.global_config = config_manager.get_global_config()
        self.results = {}
        self.logger = logging.getLogger(__name__)
    
    async def run_diagnostics(self, project_ids: List[str] = None) -> Dict:
        """运行多项目诊断"""
        if project_ids is None:
            project_ids = self.config_manager.get_enabled_projects()
        
        self.logger.info(f"开始诊断项目: {', '.join(project_ids)}")
        
        # 并行执行项目诊断
        tasks = []
        for project_id in project_ids:
            task = self._run_project_diagnostics(project_id)
            tasks.append(task)
        
        project_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        for project_id, result in zip(project_ids, project_results):
            if isinstance(result, Exception):
                self.results[project_id] = {
                    'status': 'error',
                    'error': str(result)
                }
                self.logger.error(f"项目 {project_id} 诊断失败: {result}")
            else:
                self.results[project_id] = result
        
        return self.results
    
    async def _run_project_diagnostics(self, project_id: str) -> Dict:
        """运行单个项目诊断"""
        project_config = self.config_manager.get_project_config(project_id)
        if not project_config:
            raise ValueError(f"未找到项目配置: {project_id}")
        
        project_results = {
            'project_id': project_id,
            'project_name': project_config['project']['name'],
            'checks': {},
            'summary': {}
        }
        
        checks_config = project_config.get('checks', {})
        
        # 运行启用的检测模块
        if checks_config.get('network', {}).get('enabled', False):
            detector = NetworkDetector(checks_config['network']['config'])
            project_results['checks']['network'] = await detector.detect_async()
        
        if checks_config.get('environment', {}).get('enabled', False):
            detector = EnvironmentDetector(checks_config['environment']['config'])
            project_results['checks']['environment'] = await detector.detect_async()
        
        if checks_config.get('paths', {}).get('enabled', False):
            detector = PathDetector(checks_config['paths']['config'])
            project_results['checks']['paths'] = await detector.detect_async()
        
        if checks_config.get('virtualenv', {}).get('enabled', False):
            install_path = project_config['project']['paths']['install_path']
            detector = VirtualEnvDetector(install_path, checks_config['virtualenv']['config'])
            project_results['checks']['virtualenv'] = await detector.detect_async()
        
        if checks_config.get('game_settings', {}).get('enabled', False):
            detector = GameSettingDetector(checks_config['game_settings']['config'])
            project_results['checks']['game_settings'] = await detector.detect_game_settings(project_id)
        
        # 生成项目摘要
        project_results['summary'] = self._generate_project_summary(project_results['checks'])
        
        return project_results
    
    def _generate_project_summary(self, checks_results: Dict) -> Dict:
        """生成项目检测摘要"""
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warning_checks = 0
        
        for check_type, result in checks_results.items():
            if 'summary' in result:
                summary = result['summary']
                total_checks += summary.get('total_checks', 0)
                passed_checks += summary.get('passed_checks', 0)
                failed_checks += summary.get('failed_checks', 0)
                warning_checks += summary.get('warning_checks', 0)
        
        return {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'warning_checks': warning_checks,
            'success_rate': passed_checks / total_checks if total_checks > 0 else 0
        }
    
    def generate_combined_report(self) -> Dict:
        """生成合并报告"""
        total_projects = len(self.results)
        projects_passed = 0
        projects_failed = 0
        projects_with_warnings = 0
        
        for project_id, result in self.results.items():
            if result.get('status') == 'error':
                projects_failed += 1
            else:
                summary = result.get('summary', {})
                if summary.get('failed_checks', 0) > 0:
                    projects_failed += 1
                elif summary.get('warning_checks', 0) > 0:
                    projects_with_warnings += 1
                else:
                    projects_passed += 1
        
        return {
            'summary': {
                'total_projects': total_projects,
                'projects_passed': projects_passed,
                'projects_failed': projects_failed,
                'projects_with_warnings': projects_with_warnings,
                'overall_success_rate': projects_passed / total_projects if total_projects > 0 else 0
            },
            'project_details': self.results,
            'recommendations': self._generate_combined_recommendations()
        }
    
    def _generate_combined_recommendations(self) -> List[str]:
        """生成合并改进建议"""
        recommendations = []
        
        for project_id, result in self.results.items():
            if result.get('status') == 'error':
                recommendations.append(f"{project_id}: 诊断过程出错 - {result.get('error')}")
            else:
                for check_type, check_result in result.get('checks', {}).items():
                    if 'recommendations' in check_result:
                        for rec in check_result['recommendations']:
                            recommendations.append(f"{project_id} - {check_type}: {rec}")
        
        return recommendations
```

### 5. 命令行接口优化

```python
# oops/cli/advanced_cli.py
import argparse
import sys
from pathlib import Path
from ..core.advanced_config_manager import AdvancedConfigManager
from ..core.multi_project_suite import MultiProjectSuite

def main():
    parser = argparse.ArgumentParser(
        description='OOPS - 多项目开源一键问题排查器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 快速扫描所有启用项目
  oops --profile quick_scan
  
  # 完整扫描指定项目
  oops --projects zenless_zone_zero maa_assistant_arknights --profile full_scan
  
  # 仅游戏设置检测
  oops --profile game_only --projects zenless_zone_zero
  
  # 创建新项目配置
  oops --create-project my_new_project --name "我的新项目" --type game_script
        """
    )
    
    # 项目选择
    project_group = parser.add_argument_group('项目选择')
    project_group.add_argument(
        '--projects', '-p',
        nargs='+',
        help='指定要检测的项目ID'
    )
    project_group.add_argument(
        '--all-projects', '-a',
        action='store_true',
        help='检测所有启用的项目'
    )
    
    # 检测配置
    config_group = parser.add_argument_group('检测配置')
    config_group.add_argument(
        '--profile', '-f',
        choices=['quick_scan', 'full_scan', 'game_only'],
        default='quick_scan',
        help='检测配置文件'
    )
    config_group.add_argument(
        '--master-config', '-m',
        default='oops_master.yaml',
        help='主配置文件路径'
    )
    
    # 项目管理
    management_group = parser.add_argument_group('项目管理')
    management_group.add_argument(
        '--create-project',
        metavar='PROJECT_ID',
        help='创建新项目配置模板'
    )
    management_group.add_argument(
        '--project-name',
        help='新项目名称（用于 --create-project）'
    )
    management_group.add_argument(
        '--project-type',
        choices=['game_script', 'yolo_project', 'generic'],
        default='generic',
        help='新项目类型（用于 --create-project）'
    )
    management_group.add_argument(
        '--list-projects',
        action='store_true',
        help='列出所有可用项目'
    )
    
    # 输出选项
    output_group = parser.add_argument_group('输出选项')
    output_group.add_argument(
        '--output', '-o',
        help='报告输出目录'
    )
    output_group.add_argument(
        '--report-format',
        choices=['html', 'json', 'text'],
        default='html',
        help='报告格式'
    )
    output_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化配置管理器
        config_manager = AdvancedConfigManager(args.master_config)
        
        # 项目管理命令
        if args.create_project:
            project_info = {
                'name': args.project_name or args.create_project,
                'type': args.project_type,
                'description': f"自动创建的 {args.create_project} 项目配置"
            }
            config_path = config_manager.create_project_template(args.create_project, project_info)
            print(f"已创建项目配置: {config_path}")
            return 0
        
        if args.list_projects:
            enabled_projects = config_manager.get_enabled_projects()
            all_projects = config_manager.master_config.get('projects', {}).keys()
            print("可用项目:")
            for project_id in all_projects:
                status = "✓ 启用" if project_id in enabled_projects else "✗ 禁用"
                print(f"  {project_id}: {status}")
            return 0
        
        # 设置检测配置文件
        config_manager.set_active_profile(args.profile)
        
        # 确定要检测的项目
        if args.projects:
            project_ids = args.projects
        elif args.all_projects:
            project_ids = config_manager.get_enabled_projects()
        else:
            project_ids = config_manager.get_enabled_projects()
        
        if not project_ids:
            print("错误: 没有启用的项目可检测")
            return 1
        
        # 创建诊断套件并运行
        suite = MultiProjectSuite(config_manager)
        
        print(f"开始检测 {len(project_ids)} 个项目...")
        results = suite.run_diagnostics(project_ids)
        
        # 生成报告
        combined_report = suite.generate_combined_report()
        
        # 输出摘要
        summary = combined_report['summary']
        print(f"\n检测完成!")
        print(f"总项目数: {summary['total_projects']}")
        print(f"通过项目: {summary['projects_passed']}")
        print(f"失败项目: {summary['projects_failed']}")
        print(f"警告项目: {summary['projects_with_warnings']}")
        print(f"总体成功率: {summary['overall_success_rate']:.1%}")
        
        return 0 if summary['projects_failed'] == 0 else 1
        
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

## 架构优势

### 1. **集中管理**
- 单一主配置文件控制所有项目
- 统一的启用/禁用机制
- 全局设置和项目特定设置的分离

### 2. **灵活配置**
- 检测配置文件支持不同使用场景
- 项目级覆盖配置
- 运行时动态启用/禁用检测模块

### 3. **易于扩展**
- 模板化项目配置创建
- 插件化检测模块
- 支持快速添加新项目

### 4. **智能复用**
- 相似项目可以共享基础配置
- 检测逻辑复用，减少重复代码
- 配置继承和覆盖机制

### 5. **用户友好**
- 简洁的命令行接口
- 清晰的配置结构
- 详细的报告和推荐

这个优化后的架构能够很好地支持多个项目的检测需求，同时保持了配置的灵活性和可维护性。通过分层配置系统和项目级覆盖机制，可以轻松管理 ZenlessZoneZero-OneDragon、MaaAssistantArknights、ok-wuthering-waves 等不同项目的检测需求。

## 📁 项目文件结构

### 完整的项目文件树
```
OOPS/
├── oops/                          # 核心Python包
│   ├── core/                      # 核心框架
│   │   ├── __init__.py
│   │   ├── advanced_config_manager.py  # 高级配置管理器
│   │   ├── multi_project_suite.py      # 多项目诊断套件
│   │   └── base_detector.py            # 检测器基类
│   ├── detectors/                 # 检测器模块
│   │   ├── __init__.py
│   │   ├── network_detector.py    # 网络连通性检测
│   │   ├── environment_detector.py # 环境依赖检测
│   │   ├── path_detector.py       # 路径规范检测
│   │   ├── virtualenv_detector.py # 虚拟环境检测
│   │   └── git/                   # Git检测组件
│   │       ├── __init__.py
│   │       ├── git_client.py
│   │       ├── pygit2_client.py
│   │       ├── gitpython_client.py
│   │       └── commandline_client.py
│   ├── plugins/                   # 插件系统
│   │   ├── __init__.py
│   │   └── game_setting_detector/ # 游戏设置检测插件
│   │       ├── __init__.py
│   │       ├── game_setting_detector.py
│   │       └── strategies/        # 检测策略
│   │           ├── __init__.py
│   │           ├── detection_strategy.py
│   │           ├── yolo_strategy.py
│   │           ├── image_recognition_strategy.py
│   │           └── coordinate_fallback_strategy.py
│   ├── reporters/                 # 报告生成器
│   │   ├── __init__.py
│   │   ├── html_reporter.py
│   │   ├── json_reporter.py
│   │   └── text_reporter.py
│   ├── utils/                     # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── network_utils.py
│   │   └── screenshot_utils.py
│   └── cli/                       # 命令行接口
│       ├── __init__.py
│       └── advanced_cli.py
├── configs/                       # 配置文件目录
│   ├── oops_master.yaml           # 主配置文件
│   ├── git_detection.yaml         # Git检测配置
│   ├── virtualenv_detection.yaml  # 虚拟环境检测配置
│   └── game_setting_detection.yaml # 游戏设置检测配置
├── projects/                      # 项目配置文件
│   ├── _template.yaml             # 项目配置模板
│   ├── zenless_zone_zero.yaml     # 绝区零一条龙配置
│   ├── maa_assistant_arknights.yaml # MAA明日方舟助手配置
│   └── ok_wuthering_waves.yaml    # 鸣潮配置
├── assets/                        # 资源文件
│   ├── models/                    # 模型文件
│   │   └── yolo/                  # YOLO模型
│   │       └── game_ui_detector.pt
│   └── templates/                 # 图像模板
│       ├── settings_icon.png
│       ├── resolution_1080p.png
│       └── frame_rate_60.png
├── knowledge_base/                # 知识库系统
│   └── zenless_zone_zero_knowledge.md
├── docs/                          # 文档目录
│   ├── README.md                  # 项目说明
│   ├── FEATURE_LIST.md            # 功能清单
│   ├── DEVELOPER_GUIDE.md         # 开发者指南
│   ├── project_structure.md       # 项目结构
│   ├── functional_design.md       # 功能设计
│   ├── multi_project_architecture.md # 多项目架构
│   ├── game_setting_detection.md  # 游戏设置检测
│   ├── unified_git_detection.md   # Git统一检测
│   ├── virtualenv_detection.md    # 虚拟环境检测
│   ├── game_setting_yolo_fallback.md # YOLO回退机制
│   └── game_setting_yaml_template.md # YAML配置模板
├── tests/                         # 测试代码
│   ├── __init__.py
│   ├── test_network_detector.py
│   ├── test_environment_detector.py
│   └── integration/               # 集成测试
│       └── test_full_diagnostic.py
├── scripts/                       # 构建和部署脚本
│   ├── build_exe.py               # EXE打包脚本
│   └── install_dependencies.bat   # 依赖安装脚本
├── requirements.txt               # Python依赖
├── requirements-dev.txt           # 开发依赖
├── setup.py                       # 安装配置
├── pyproject.toml                 # 项目配置
└── oops.py                        # 主程序入口
```

### 配置文件结构详解

#### 主配置文件 (`oops_master.yaml`)
```
configs/
├── oops_master.yaml              # 主配置 - 控制全局设置和项目启用状态
├── git_detection.yaml            # Git检测模块配置
├── virtualenv_detection.yaml     # 虚拟环境检测配置
├── network_detection.yaml        # 网络连通性检测配置
├── environment_detection.yaml    # 环境依赖检测配置
├── path_detection.yaml           # 路径规范检测配置
└── game_setting_detection.yaml   # 游戏设置检测配置
```

#### 项目配置文件 (`projects/`)
```
projects/
├── _template.yaml                # 项目配置模板
├── zenless_zone_zero.yaml        # 绝区零一条龙
├── maa_assistant_arknights.yaml  # MAA明日方舟助手
├── ok_wuthering_waves.yaml       # 鸣潮
├── genshin_impact.yaml           # 原神（示例）
└── star_rail.yaml                # 星穹铁道（示例）
```

#### 资源文件结构 (`assets/`)
```
assets/
├── models/                       # 机器学习模型
│   └── yolo/
│       ├── game_ui_detector.pt   # 游戏UI检测模型
│       └── settings_detector.pt  # 设置界面检测模型
└── templates/                    # 图像识别模板
    ├── common/                   # 通用模板
    │   ├── settings_icon.png
    │   ├── back_button.png
    │   └── apply_button.png
    ├── zzz/                      # 绝区零专用模板
    │   ├── zzz_settings_icon.png
    │   └── zzz_display_tab.png
    └── maa/                      # MAA专用模板
        ├── maa_settings_icon.png
        └── maa_graphics_tab.png
```

### 核心代码模块说明

#### 配置管理系统
- `oops/core/advanced_config_manager.py` - 高级配置管理器，支持多项目和配置覆盖
- `oops/core/multi_project_suite.py` - 多项目诊断套件，并行执行项目检测

#### 检测器模块
- `oops/detectors/network_detector.py` - 网络连通性检测
- `oops/detectors/environment_detector.py` - 环境依赖检测
- `oops/detectors/path_detector.py` - 路径规范检测
- `oops/detectors/virtualenv_detector.py` - 虚拟环境检测

#### Git检测组件
- `oops/detectors/git/git_client.py` - Git客户端抽象基类
- `oops/detectors/git/pygit2_client.py` - PyGit2客户端实现
- `oops/detectors/git/gitpython_client.py` - GitPython客户端实现
- `oops/detectors/git/commandline_client.py` - 命令行Git客户端实现

#### 游戏设置检测插件
- `oops/plugins/game_setting_detector/game_setting_detector.py` - 游戏设置检测主类
- `oops/plugins/game_setting_detector/strategies/` - 检测策略
  - `detection_strategy.py` - 检测策略基类
  - `yolo_strategy.py` - YOLO对象检测策略
  - `image_recognition_strategy.py` - 图像识别策略
  - `coordinate_fallback_strategy.py` - 坐标回退策略

### 部署和运行文件

#### 可执行文件构建
- `scripts/build_exe.py` - 将Python代码打包为可执行文件
- `scripts/install_dependencies.bat` - Windows依赖安装脚本

#### 依赖管理
- `requirements.txt` - 生产环境依赖
- `requirements-dev.txt` - 开发环境依赖
- `setup.py` - Python包安装配置
- `pyproject.toml` - 现代Python项目配置

### 文档结构

#### 核心文档
- `README.md` - 项目说明和快速开始
- `FEATURE_LIST.md` - 完整功能清单
- `DEVELOPER_GUIDE.md` - 开发者入门指南

#### 设计文档
- `project_structure.md` - 项目架构和文件结构
- `functional_design.md` - 功能模块详细设计
- `multi_project_architecture.md` - 多项目支持架构
- `game_setting_detection.md` - 游戏设置检测实现

#### 技术文档
- `unified_git_detection.md` - Git统一检测系统设计
- `virtualenv_detection.md` - 虚拟环境检测系统设计
- `game_setting_yolo_fallback.md` - YOLO回退机制设计
- `game_setting_yaml_template.md` - YAML配置模板

#### 知识库
- `knowledge_base/zenless_zone_zero_knowledge.md` - 绝区零项目知识库

### 开发工作流

#### 代码开发
```
1. 修改源代码 (oops/ 目录)
2. 运行测试 (tests/ 目录)
3. 更新文档 (docs/ 目录)
4. 构建可执行文件 (scripts/build_exe.py)
```

#### 配置管理
```
1. 修改主配置 (configs/oops_master.yaml)
2. 添加项目配置 (projects/ 目录)
3. 更新检测配置 (configs/ 目录)
4. 测试配置变更
```

#### 资源管理
```
1. 添加新模型 (assets/models/)
2. 添加模板图像 (assets/templates/)
3. 更新知识库 (knowledge_base/)
```

这个完整的文件结构确保了项目的可维护性和扩展性，支持多项目管理和复杂的检测功能。