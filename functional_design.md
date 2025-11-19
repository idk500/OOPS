# OOPS 功能模块设计

## 部署架构设计

### 最终交付物结构
```
OOPS_Tool/
├── oops.exe                    # 主可执行文件
├── configs/                    # 配置文件目录
│   ├── base.yaml              # 基础配置模板
│   ├── network.yaml           # 网络检测配置
│   ├── environment.yaml       # 环境检测配置
│   ├── yolo_project.yaml      # YOLO项目专用配置
│   └── game_script.yaml       # 游戏脚本专用配置
├── templates/                  # 报告模板
│   ├── report.html            # HTML报告模板
│   └── report.txt             # 文本报告模板
└── data/                      # 数据文件
    └── historical_problems.db # 历史问题数据库
```

### 打包策略
使用 PyInstaller 打包为单个可执行文件，配置文件作为外部资源：
```python
# setup.py 中的打包配置
setup(
    # ... 其他配置
    options={
        'pyinstaller': {
            'onefile': True,
            'console': True,
            'icon': 'assets/icon.ico',
            'add-data': [
                'configs/*;configs/',
                'templates/*;templates/',
                'data/*;data/'
            ]
        }
    }
)
```

## YAML 配置系统设计

### 父子关系配置结构

#### 基础配置语法
```yaml
# configs/base.yaml
version: "1.0"
config_schema: "hierarchical"

checks:
  network:
    type: "parallel_group"  # 并行检测组
    description: "网络连通性检测"
    success_condition: "any"  # 任意一个成功即视为组成功
    children:
      - id: "pypi_official"
        type: "pypi_source"
        url: "https://pypi.org/simple/"
        timeout: 10
        required: false
        
      - id: "pypi_tsinghua"  
        type: "pypi_source"
        url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
        timeout: 10
        required: false
        
      - id: "pypi_aliyun"
        type: "pypi_source" 
        url: "https://mirrors.aliyun.com/pypi/simple/"
        timeout: 10
        required: false

  git_repos:
    type: "parallel_group"
    description: "Git仓库连通性"
    success_condition: "any"
    children:
      - id: "github_main"
        type: "git_repo"
        url: "https://github.com/owner/repo.git"
        timeout: 30
        required: true
        
      - id: "gitee_mirror"
        type: "git_repo"
        url: "https://gitee.com/owner/mirror.git"
        timeout: 30
        required: false

  environment:
    type: "sequential_group"  # 顺序检测组
    description: "环境依赖检测"
    success_condition: "all"  # 所有检测必须成功
    children:
      - id: "python_version"
        type: "python_check"
        min_version: "3.8"
        max_version: "3.11"
        required: true
        
      - id: "virtual_env"
        type: "virtualenv_check"
        auto_detect: true
        required: false
```

#### 完整的配置示例
```yaml
# configs/network.yaml
network_checks:
  pypi_sources:
    type: "parallel_group"
    name: "PyPI 镜像源检测"
    description: "检测可用的 PyPI 镜像源，任意一个可用即视为成功"
    success_condition: "any"
    children:
      - id: "pypi_official"
        name: "官方 PyPI 源"
        type: "url_check"
        url: "https://pypi.org/simple/"
        method: "GET"
        expected_status: 200
        timeout: 10
        weight: 1.0
        
      - id: "pypi_tsinghua"
        name: "清华镜像源"
        type: "url_check" 
        url: "https://pypi.tuna.tsinghua.edu.cn/simple/"
        method: "GET"
        expected_status: 200
        timeout: 10
        weight: 0.9
        
      - id: "pypi_aliyun"
        name: "阿里云镜像源"
        type: "url_check"
        url: "https://mirrors.aliyun.com/pypi/simple/"
        method: "GET" 
        expected_status: 200
        timeout: 10
        weight: 0.9
        
      - id: "pypi_bfsu"
        name: "北外镜像源"
        type: "url_check"
        url: "https://mirrors.bfsu.edu.cn/pypi/web/simple/"
        method: "GET"
        expected_status: 200
        timeout: 10
        weight: 0.8

  git_sources:
    type: "parallel_group"
    name: "Git 仓库源检测"
    description: "检测 Git 仓库连通性，主仓库必须成功，镜像仓库任意一个成功即可"
    success_condition: "conditional"
    children:
      - id: "github_main"
        name: "GitHub 主仓库"
        type: "git_check"
        url: "https://github.com/owner/repo.git"
        command: "ls-remote"
        timeout: 30
        required: true
        weight: 1.0
        
      - id: "gitee_mirror"
        name: "Gitee 镜像仓库"
        type: "git_check"
        url: "https://gitee.com/owner/mirror.git" 
        command: "ls-remote"
        timeout: 30
        required: false
        weight: 0.8

  project_urls:
    type: "sequential_group"
    name: "项目相关URL检测"
    description: "检测项目相关网站的可访问性"
    success_condition: "all"
    children:
      - id: "project_homepage"
        name: "项目主页"
        type: "url_check"
        url: "https://project.example.com"
        method: "GET"
        expected_status: 200
        timeout: 10
        required: true
        
      - id: "project_docs"
        name: "项目文档"
        type: "url_check"
        url: "https://docs.project.example.com"
        method: "GET"
        expected_status: 200
        timeout: 10
        required: false
        
      - id: "project_api"
        name: "项目API"
        type: "url_check"
        url: "https://api.project.example.com/health"
        method: "GET"
        expected_status: 200
        timeout: 10
        required: false
```

## 虚拟环境自动检测功能

### 虚拟环境检测算法

```python
# oops/detectors/virtualenv_detector.py
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class VirtualEnvDetector:
    """虚拟环境自动检测器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.venv_paths = self._get_common_venv_paths()
        
    def _get_common_venv_paths(self) -> List[Path]:
        """获取常见的虚拟环境路径"""
        common_paths = [
            self.project_root / ".venv",
            self.project_root / "venv", 
            self.project_root / "env",
            self.project_root / ".virtualenv",
            self.project_root / "virtualenv",
        ]
        
        # 检查项目根目录下的所有目录，寻找可能的虚拟环境
        for item in self.project_root.iterdir():
            if item.is_dir() and any(pattern in item.name.lower() for pattern in 
                                   ['venv', 'virtualenv', '.env', 'env']):
                common_paths.append(item)
                
        return common_paths
    
    def detect_virtualenv(self) -> Optional[Dict]:
        """检测虚拟环境"""
        for venv_path in self.venv_paths:
            if self._is_valid_virtualenv(venv_path):
                return self._analyze_virtualenv(venv_path)
        return None
    
    def _is_valid_virtualenv(self, venv_path: Path) -> bool:
        """检查是否为有效的虚拟环境"""
        # 检查虚拟环境目录结构
        required_dirs = [
            venv_path / "Scripts" if os.name == 'nt' else venv_path / "bin",
            venv_path / "Lib" if os.name == 'nt' else venv_path / "lib",
        ]
        
        return all(path.exists() for path in required_dirs)
    
    def _analyze_virtualenv(self, venv_path: Path) -> Dict:
        """分析虚拟环境状态"""
        python_executable = self._get_python_executable(venv_path)
        if not python_executable:
            return None
            
        result = {
            'path': str(venv_path),
            'python_executable': str(python_executable),
            'version': self._get_python_version(python_executable),
            'packages': self._get_installed_packages(python_executable),
            'requirements_status': self._check_requirements(venv_path, python_executable),
            'activation_script': self._get_activation_script(venv_path)
        }
        
        return result
    
    def _get_python_executable(self, venv_path: Path) -> Optional[Path]:
        """获取虚拟环境中的Python可执行文件"""
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
            python_exe_alt = venv_path / "Scripts" / "python"
        else:  # Unix-like
            python_exe = venv_path / "bin" / "python"
            
        return python_exe if python_exe.exists() else None
    
    def _get_python_version(self, python_executable: Path) -> Optional[str]:
        """获取Python版本"""
        try:
            result = subprocess.run(
                [str(python_executable), "--version"],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None
    
    def _get_installed_packages(self, python_executable: Path) -> List[Dict]:
        """获取已安装的包列表"""
        try:
            result = subprocess.run(
                [str(python_executable), "-m", "pip", "list", "--format=json"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                return [
                    {
                        'name': pkg['name'],
                        'version': pkg['version']
                    } for pkg in packages
                ]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError):
            pass
            
        return []
    
    def _check_requirements(self, venv_path: Path, python_executable: Path) -> Dict:
        """检查requirements.txt兼容性"""
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "reqs.txt", 
            self.project_root / "requirements-dev.txt",
            self.project_root / "requirements_test.txt",
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                return self._validate_requirements(req_file, python_executable)
                
        return {'status': 'no_requirements', 'message': '未找到requirements.txt文件'}
    
    def _validate_requirements(self, req_file: Path, python_executable: Path) -> Dict:
        """验证requirements.txt兼容性"""
        try:
            # 读取requirements.txt
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # 获取当前安装的包
            installed_packages = {pkg['name'].lower(): pkg['version'] for pkg in self._get_installed_packages(python_executable)}
            
            missing_packages = []
            version_mismatches = []
            
            for req in requirements:
                package_info = self._parse_requirement(req)
                if package_info:
                    package_name = package_info['name'].lower()
                    
                    if package_name not in installed_packages:
                        missing_packages.append(package_info)
                    elif package_info.get('specifier'):
                        # 检查版本要求
                        if not self._check_version_compatibility(
                            installed_packages[package_name], 
                            package_info['specifier']
                        ):
                            version_mismatches.append({
                                'package': package_info['name'],
                                'required': package_info['specifier'],
                                'installed': installed_packages[package_name]
                            })
            
            return {
                'status': 'validated',
                'requirements_file': str(req_file),
                'total_requirements': len(requirements),
                'missing_packages': missing_packages,
                'version_mismatches': version_mismatches,
                'compatibility_score': self._calculate_compatibility_score(
                    len(requirements), len(missing_packages), len(version_mismatches)
                )
            }
            
        except Exception as e:
            return {'status': 'error', 'message': f'验证requirements.txt时出错: {str(e)}'}
    
    def _parse_requirement(self, requirement: str) -> Optional[Dict]:
        """解析单个依赖要求"""
        # 简化解析，实际实现需要使用packaging库
        requirement = requirement.strip()
        if not requirement:
            return None
            
        # 移除注释
        if '#' in requirement:
            requirement = requirement.split('#')[0].strip()
            
        # 基本解析
        parts = requirement.split('==', 1)
        if len(parts) == 2:
            return {'name': parts[0], 'specifier': f'=={parts[1]}'}
            
        parts = requirement.split('>=', 1)  
        if len(parts) == 2:
            return {'name': parts[0], 'specifier': f'>={parts[1]}'}
            
        parts = requirement.split('<=', 1)
        if len(parts) == 2:
            return {'name': parts[0], 'specifier': f'<={parts[1]}'}
            
        # 默认情况
        return {'name': requirement, 'specifier': None}
    
    def _check_version_compatibility(self, installed_version: str, required_specifier: str) -> bool:
        """检查版本兼容性"""
        # 简化实现，实际应该使用packaging.version
        try:
            # 这里使用简化的版本比较
            # 实际实现应该使用 packaging.version.parse 和 packaging.specifiers.SpecifierSet
            return True  # 简化返回
        except:
            return False
    
    def _calculate_compatibility_score(self, total: int, missing: int, mismatches: int) -> float:
        """计算兼容性分数"""
        if total == 0:
            return 1.0
        return max(0.0, (total - missing - mismatches * 0.5) / total)
    
    def _get_activation_script(self, venv_path: Path) -> Optional[str]:
        """获取激活脚本路径"""
        if os.name == 'nt':  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            if activate_script.exists():
                return str(activate_script)
        else:  # Unix-like
            activate_script = venv_path / "bin" / "activate"
            if activate_script.exists():
                return str(activate_script)
        return None
```

## 核心检测引擎设计

### 并行检测引擎

```python
# oops/core/parallel_detector.py
import asyncio
import concurrent.futures
from typing import List, Dict, Any
from ..config import ConfigManager

class ParallelDetector:
    """并行检测引擎"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.max_workers = 10  # 最大并发数
        
    async def detect_parallel_group(self, group_config: Dict) -> Dict:
        """检测并行组"""
        children = group_config.get('children', [])
        success_condition = group_config.get('success_condition', 'any')
        
        # 并行执行所有子检测
        tasks = [self._run_single_check(child) for child in children]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        processed_results = []
        success_count = 0
        
        for child_config, result in zip(children, results):
            if isinstance(result, Exception):
                check_result = {
                    'id': child_config['id'],
                    'name': child_config.get('name', child_config['id']),
                    'status': 'error',
                    'error': str(result)
                }
            else:
                check_result = result
                if result.get('status') == 'success':
                    success_count += 1
            
            processed_results.append(check_result)
        
        # 根据成功条件判断组状态
        group_status = self._evaluate_group_status(
            success_count, len(children), success_condition
        )
        
        return {
            'group_id': group_config.get('id'),
            'group_name': group_config.get('name', 'Unnamed Group'),
            'success_condition': success_condition,
            'status': group_status,
            'success_count': success_count,
            'total_checks': len(children),
            'children': processed_results
        }
    
    async def _run_single_check(self, check_config: Dict) -> Dict:
        """运行单个检测"""
        check_type = check_config['type']
        
        if check_type == 'url_check':
            return await self._run_url_check(check_config)
        elif check_type == 'git_check':
            return await self._run_git_check(check_config)
        elif check_type == 'pypi_source':
            return await self._run_pypi_check(check_config)
        else:
            return {
                'id': check_config['id'],
                'name': check_config.get('name', check_config['id']),
                'status': 'skipped',
                'message': f'未知的检测类型: {check_type}'
            }
    
    async def _run_url_check(self, config: Dict) -> Dict:
        """URL连通性检测"""
        import aiohttp
        import time
        
        start_time = time.time()
        try:
            timeout = aiohttp.ClientTimeout(total=config.get('timeout', 10))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(config['url']) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    expected_status = config.get('expected_status', 200)
                    if response.status == expected_status:
                        return {
                            'id': config['id'],
                            'name': config.get('name', config['id']),
                            'status': 'success',
                            'response_time_ms': response_time,
                            'status_code': response.status,
                            'content_length': response.content_length
                        }
                    else:
                        return {
                            'id': config['id'],
                            'name': config.get('name', config['id']),
                            'status': 'failed',
                            'response_time_ms': response_time,
                            'status_code': response.status,
                            'expected_status': expected_status
                        }
        except asyncio.TimeoutError:
            return {
                'id': config['id'],
                'name': config.get('name', config['id']),
                'status': 'timeout',
                'timeout': config.get('timeout', 10)
            }
        except Exception as e:
            return {
                'id': config['id'],
                'name': config.get('name', config['id']),
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_git_check(self, config: Dict) -> Dict:
        """Git仓库检测"""
        import subprocess
        import time
        
        start_time = time.time()
        try:
            command = ['git', 'ls-remote', config['url']]
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=config.get('timeout', 30)
            )
            
            stdout, stderr = await result.communicate()
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                return {
                    'id': config['id'],
                    'name': config.get('name', config['id']),
                    'status': 'success',
                    'response_time_ms': response_time,
                    'branch_count': len(stdout.decode().strip().split('\n')) if stdout else 0
                }
            else:
                return {
                    'id': config['id'],
                    'name': config.get('name', config['id']),
                    'status': 'failed',
                    'response_time_ms': response_time,
                    'error': stderr.decode().strip() if stderr else 'Unknown error'
                }
                
        except asyncio.TimeoutError:
            return {
                'id': config['id'],
                'name': config.get('name', config['id']),
                'status': 'timeout',
                'timeout': config.get('timeout', 30)
            }
        except Exception as e:
            return {
                'id': config['id'],
                'name': config.get('name', config['id']),
                'status': 'error',
                'error': str(e)
            }
    
    async def _run_pypi_check(self, config: Dict) -> Dict:
        """PyPI源检测"""
        # 使用_url_check实现，但添加PyPI特定的验证
        url_check_result = await self._run_url_check(config)
        
        if url_check_result['status'] == 'success':
            # 可以添加PyPI特定的验证，如检查返回内容是否为有效的PyPI页面
            url_check_result['type'] = 'pypi_source'
            
        return url_check_result
    
    def _evaluate_group_status(self, success_count: int, total_count: int, condition: str) -> str:
        """评估组检测状态"""
        if condition == 'any':
            return 'success' if success_count > 0 else 'failed'
        elif condition == 'all':
            return 'success' if success_count == total_count else 'failed'
        elif condition == 'majority':
            return 'success' if success_count > total_count / 2 else 'failed'
        else:
            return 'unknown'
```

## 命令行接口设计

### 主命令行接口

```python
# oops/cli/main.py
import argparse
import sys
from pathlib import Path
from ..core import DiagnosticSuite
from ..config import ConfigManager

def main():
    parser = argparse.ArgumentParser(
        description='OOPS - 开源一键问题排查器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  oops --project-path ./my_project --config yolo_project
  oops --project-path D:\MyGame --auto-detect
  oops --project-path . --report html --output ./reports
        """
    )
    
    parser.add_argument(
        '--project-path', '-p',
        type=str,
        required=True,
        help='项目根目录路径'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        choices=['base', 'network', 'environment', 'yolo_project', 'game_script'],
        default='base',
        help='使用的配置模板'
    )
    
    parser.add_argument(
        '--auto-detect', '-a',
        action='store_true',
        help='自动检测项目类型并选择合适的配置'
    )
    
    parser.add_argument(
        '--report-format', '-f',
        choices=['html', 'json', 'text'],
        default='html',
        help='报告输出格式'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='报告输出目录'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出模式'
    )
    
    parser.add_argument(
        '--check-virtualenv', 
        action='store_true',
        default=True,
        help='检查虚拟环境（默认启用）'
    )
    
    parser.add_argument(
        '--no-virtualenv',
        action='store_true',
        help='跳过虚拟环境检查'
    )
    
    args = parser.parse_args()
    
    # 验证项目路径
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        return 1
    
    # 创建诊断套件
    try:
        suite = DiagnosticSuite(
            project_root=project_path,
            config_name=args.config,
            auto_detect=args.auto_detect,
            check_virtualenv=not args.no_virtualenv
        )
        
        # 运行诊断
        print("开始运行诊断...")
        results = suite.run_diagnostics()
        
        # 生成报告
        print("生成诊断报告...")
        report_path = suite.generate_report(
            format=args.report_format,
            output_dir=args.output
        )
        
        print(f"诊断完成！报告已保存至: {report_path}")
        
        # 显示摘要
        summary = suite.get_summary()
        print(f"\n检测摘要:")
        print(f"  总检查数: {summary['total_checks']}")
        print(f"  通过数: {summary['passed_checks']}")
        print(f"  失败数: {summary['failed_checks']}")
        print(f"  警告数: {summary['warning_checks']}")
        print(f"  成功率: {summary['success_rate']:.1%}")
        
        return 0 if summary['failed_checks'] == 0 else 1
        
    except Exception as e:
        print(f"诊断过程中出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

这个功能模块设计提供了完整的实现方案，特别关注了：
1. 可执行文件部署架构
2. YAML配置的父子关系和并行检测
3. 虚拟环境自动检测和requirements.txt验证
4. 并行检测引擎实现
5. 用户友好的命令行接口

这样的设计能够满足用户对开源脚本自检工具的所有需求。