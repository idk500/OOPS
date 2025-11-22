"""
配置管理模块
负责加载和管理项目配置、检测规则和用户设置
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.master_config: Dict[str, Any] = {}
        self.project_configs: Dict[str, Dict[str, Any]] = {}
        self.detection_rules: Dict[str, Any] = {}
        
    def load_master_config(self, config_path: Optional[str] = None) -> bool:
        """加载主配置文件"""
        if config_path is None:
            config_path = self.config_dir / "oops_master.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.master_config = yaml.safe_load(f)
            logger.info(f"成功加载主配置文件: {config_path}")
            return True
        except Exception as e:
            logger.error(f"加载主配置文件失败: {e}")
            return False
    
    def load_project_config(self, project_name: str, silent: bool = False) -> Optional[Dict[str, Any]]:
        """加载指定项目的配置
        
        Args:
            project_name: 项目名称
            silent: 是否静默模式（不输出警告日志）
        """
        if project_name in self.project_configs:
            return self.project_configs[project_name]
            
        config_path = self.config_dir / f"{project_name}.yaml"
        if not config_path.exists():
            if not silent:
                logger.warning(f"项目配置文件不存在: {config_path}")
            return None
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.project_configs[project_name] = config
            logger.info(f"成功加载项目配置: {project_name}")
            return config
        except Exception as e:
            logger.error(f"加载项目配置失败 {project_name}: {e}")
            return None
    
    def get_enabled_projects(self) -> List[str]:
        """获取启用的项目列表"""
        if not self.master_config:
            return []
            
        projects = self.master_config.get('projects', {})
        return [name for name, config in projects.items() 
                if config.get('enabled', False)]
    
    def get_project_config(self, project_name: str, silent: bool = False) -> Optional[Dict[str, Any]]:
        """获取项目配置，如果未加载则自动加载
        
        Args:
            project_name: 项目名称
            silent: 是否静默模式（不输出警告日志）
        """
        if project_name not in self.project_configs:
            return self.load_project_config(project_name, silent=silent)
        return self.project_configs.get(project_name)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置的完整性"""
        required_fields = ['project', 'checks']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"配置缺少必需字段: {field}")
                return False
                
        project_info = config.get('project', {})
        if 'name' not in project_info or 'type' not in project_info:
            logger.error("项目配置缺少名称或类型")
            return False
            
        return True
    
    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置模板"""
        return {
            'project': {
                'name': '未命名项目',
                'type': 'generic',
                'description': '项目描述',
                'paths': {
                    'install_path': '',
                    'config_path': '',
                }
            },
            'checks': {
                'network': {
                    'enabled': True,
                    'git_repos': [],
                    'pypi_sources': [],
                    'mirror_sites': [],
                    'project_websites': [],
                },
                'environment': {
                    'enabled': True,
                    'python_version': '>=3.8',
                    'virtual_env': True,
                    'system_libraries': [],
                },
                'paths': {
                    'enabled': True,
                    'check_chinese_paths': True,
                    'check_permissions': True,
                    'check_path_length': True,
                },
                'hardware': {
                    'enabled': False,
                    'check_ram': True,
                    'check_disk': True,
                    'check_gpu': False,
                }
            },
            'report': {
                'format': 'html',
                'output_dir': 'reports',
                'include_timestamp': True,
            }
        }


class DetectionRule:
    """检测规则基类"""
    
    def __init__(self, name: str, description: str, severity: str = "info"):
        self.name = name
        self.description = description
        self.severity = severity  # info, warning, error, critical
        
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行检测，返回检测结果"""
        raise NotImplementedError("子类必须实现check方法")
    
    def get_fix_suggestion(self, result: Dict[str, Any]) -> str:
        """获取修复建议"""
        return result.get('fix_suggestion', '请参考项目文档进行修复')


class NetworkConnectivityRule(DetectionRule):
    """网络连通性检测规则"""
    
    def __init__(self):
        super().__init__(
            name="network_connectivity",
            description="检测网络连通性",
            severity="warning"
        )
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """检查网络连通性"""
        network_config = config.get('checks', {}).get('network', {})
        if not network_config.get('enabled', False):
            return {
                'status': 'skipped',
                'message': '网络检测已禁用'
            }
            
        # 这里实现具体的网络检测逻辑
        return {
            'status': 'pending',
            'message': '网络检测待实现'
        }


class EnvironmentDependencyRule(DetectionRule):
    """环境依赖检测规则"""
    
    def __init__(self):
        super().__init__(
            name="environment_dependencies",
            description="检测环境依赖",
            severity="error"
        )
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """检查环境依赖"""
        env_config = config.get('checks', {}).get('environment', {})
        if not env_config.get('enabled', False):
            return {
                'status': 'skipped',
                'message': '环境检测已禁用'
            }
            
        # 这里实现具体的环境检测逻辑
        return {
            'status': 'pending',
            'message': '环境检测待实现'
        }


def create_default_master_config() -> Dict[str, Any]:
    """创建默认主配置"""
    return {
        'version': '1.0',
        'projects': {
            'zenless_zone_zero': {
                'enabled': True,
                'config': 'configs/zenless_zone_zero.yaml',
                'description': '绝区零一条龙项目'
            },
            'maa_assistant_arknights': {
                'enabled': True,
                'config': 'configs/maa_assistant_arknights.yaml',
                'description': 'MAA明日方舟助手'
            },
            'generic_python': {
                'enabled': True,
                'config': 'configs/generic_python.yaml',
                'description': '通用Python项目'
            }
        },
        'settings': {
            'default_report_format': 'html',
            'enable_auto_fix': False,
            'log_level': 'INFO',
            'max_concurrent_checks': 5
        }
    }