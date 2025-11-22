"""
配置管理模块测试
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from oops.core.config import ConfigManager, create_default_master_config


class TestConfigManager:
    """配置管理器测试类"""
    
    def setup_method(self):
        """测试方法前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "configs"
        self.config_dir.mkdir()
        self.config_manager = ConfigManager(str(self.config_dir))
    
    def teardown_method(self):
        """测试方法后置清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_default_master_config(self):
        """测试创建默认主配置"""
        config = create_default_master_config()
        
        assert 'version' in config
        assert 'projects' in config
        assert 'settings' in config
        assert config['version'] == '1.0'
        
        # 检查项目配置
        projects = config['projects']
        assert 'zenless_zone_zero' in projects
        assert 'generic_python' in projects
        
        # 检查设置
        settings = config['settings']
        assert 'default_report_format' in settings
        assert 'log_level' in settings
    
    def test_load_master_config_success(self):
        """测试成功加载主配置文件"""
        # 创建测试配置文件
        config_data = create_default_master_config()
        config_file = self.config_dir / "oops_master.yaml"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        # 测试加载
        result = self.config_manager.load_master_config()
        assert result is True
        assert self.config_manager.master_config == config_data
    
    def test_load_master_config_file_not_found(self):
        """测试加载不存在的配置文件"""
        result = self.config_manager.load_master_config()
        assert result is False
        assert self.config_manager.master_config == {}
    
    def test_load_master_config_invalid_yaml(self):
        """测试加载无效的YAML文件"""
        config_file = self.config_dir / "oops_master.yaml"
        
        # 写入无效的YAML内容
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [\n")
        
        result = self.config_manager.load_master_config()
        assert result is False
    
    def test_load_project_config_success(self):
        """测试成功加载项目配置"""
        # 创建项目配置文件
        project_config = {
            'project': {
                'name': '测试项目',
                'type': 'test',
                'paths': {
                    'install_path': '/test/path'
                }
            },
            'checks': {
                'network': {'enabled': True},
                'environment': {'enabled': True}
            }
        }
        
        config_file = self.config_dir / "test_project.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f)
        
        # 测试加载
        result = self.config_manager.load_project_config('test_project')
        assert result == project_config
        assert 'test_project' in self.config_manager.project_configs
    
    def test_load_project_config_file_not_found(self):
        """测试加载不存在的项目配置"""
        result = self.config_manager.load_project_config('nonexistent')
        assert result is None
    
    def test_get_enabled_projects(self):
        """测试获取启用的项目列表"""
        # 创建主配置文件
        config_data = {
            'projects': {
                'project1': {'enabled': True},
                'project2': {'enabled': False},
                'project3': {'enabled': True}
            }
        }
        
        config_file = self.config_dir / "oops_master.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        self.config_manager.load_master_config()
        enabled_projects = self.config_manager.get_enabled_projects()
        
        assert 'project1' in enabled_projects
        assert 'project3' in enabled_projects
        assert 'project2' not in enabled_projects
        assert len(enabled_projects) == 2
    
    def test_validate_config_valid(self):
        """测试验证有效的配置"""
        valid_config = {
            'project': {
                'name': '测试项目',
                'type': 'test'
            },
            'checks': {
                'network': {'enabled': True}
            }
        }
        
        result = self.config_manager.validate_config(valid_config)
        assert result is True
    
    def test_validate_config_missing_project(self):
        """测试验证缺少project字段的配置"""
        invalid_config = {
            'checks': {
                'network': {'enabled': True}
            }
        }
        
        result = self.config_manager.validate_config(invalid_config)
        assert result is False
    
    def test_validate_config_missing_checks(self):
        """测试验证缺少checks字段的配置"""
        invalid_config = {
            'project': {
                'name': '测试项目',
                'type': 'test'
            }
        }
        
        result = self.config_manager.validate_config(invalid_config)
        assert result is False
    
    def test_validate_config_missing_project_name(self):
        """测试验证缺少项目名称的配置"""
        invalid_config = {
            'project': {
                'type': 'test'
            },
            'checks': {
                'network': {'enabled': True}
            }
        }
        
        result = self.config_manager.validate_config(invalid_config)
        assert result is False
    
    def test_create_default_config(self):
        """测试创建默认配置模板"""
        default_config = self.config_manager.create_default_config()
        
        assert 'project' in default_config
        assert 'checks' in default_config
        assert 'report' in default_config
        
        project_info = default_config['project']
        assert 'name' in project_info
        assert 'type' in project_info
        assert 'paths' in project_info
        
        checks = default_config['checks']
        assert 'network' in checks
        assert 'environment' in checks
        assert 'paths' in checks
    
    def test_get_project_config_cached(self):
        """测试获取已缓存的配置"""
        # 先加载配置
        project_config = {
            'project': {'name': '测试项目'},
            'checks': {'network': {'enabled': True}}
        }
        
        config_file = self.config_dir / "test_project.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(project_config, f)
        
        # 第一次加载
        result1 = self.config_manager.get_project_config('test_project')
        assert result1 == project_config
        
        # 第二次应该从缓存获取
        result2 = self.config_manager.get_project_config('test_project')
        assert result2 == project_config
        
        # 验证缓存中确实有这个项目
        assert 'test_project' in self.config_manager.project_configs


class TestDetectionRule:
    """检测规则基类测试"""
    
    def test_detection_rule_initialization(self):
        """测试检测规则初始化"""
        from oops.core.config import DetectionRule
        
        rule = DetectionRule(
            name="test_rule",
            description="测试规则",
            severity="warning"
        )
        
        assert rule.name == "test_rule"
        assert rule.description == "测试规则"
        assert rule.severity == "warning"
    
    def test_detection_rule_check_not_implemented(self):
        """测试检测规则check方法未实现"""
        from oops.core.config import DetectionRule
        
        rule = DetectionRule("test", "test")
        
        with pytest.raises(NotImplementedError):
            rule.check({})
    
    def test_detection_rule_get_fix_suggestion(self):
        """测试获取修复建议"""
        from oops.core.config import DetectionRule
        
        rule = DetectionRule("test", "test")
        result = {'fix_suggestion': '测试修复建议'}
        
        suggestion = rule.get_fix_suggestion(result)
        assert suggestion == '测试修复建议'
        
        # 测试没有修复建议的情况
        result_no_suggestion = {}
        suggestion = rule.get_fix_suggestion(result_no_suggestion)
        assert suggestion == '请参考项目文档进行修复'


class TestNetworkConnectivityRule:
    """网络连通性检测规则测试"""
    
    def setup_method(self):
        """测试方法前置设置"""
        from oops.detectors.network import NetworkConnectivityDetector
        self.rule = NetworkConnectivityDetector()
    
    def test_initialization(self):
        """测试初始化"""
        assert self.rule.name == "network_connectivity"
        assert self.rule.description == "检测网络连通性"
        assert self.rule.severity == "warning"
        assert self.rule.timeout == 10
    
    def test_check_disabled(self):
        """测试禁用网络检测"""
        config = {
            'checks': {
                'network': {'enabled': False}
            }
        }
        
        result = self.rule.check(config)
        assert result['status'] == 'skipped'
        assert '网络检测已禁用' in result['message']
    
    @pytest.mark.asyncio
    async def test_check_async_disabled(self):
        """测试异步禁用网络检测"""
        config = {
            'checks': {
                'network': {'enabled': False}
            }
        }
        
        result = await self.rule.check_async(config)
        assert result['status'] == 'skipped'
        assert '网络检测已禁用' in result['message']


if __name__ == "__main__":
    pytest.main([__file__])