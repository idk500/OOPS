"""
基础测试
验证核心模块可以正常导入和初始化
"""

import pytest


def test_imports():
    """测试核心模块导入"""
    from oops.core.config import ConfigManager
    from oops.core.diagnostics import DiagnosticSuite
    from oops.core.report import ReportGenerator
    from oops.core.default_config import DefaultConfigLoader

    assert ConfigManager is not None
    assert DiagnosticSuite is not None
    assert ReportGenerator is not None
    assert DefaultConfigLoader is not None


def test_version():
    """测试版本号"""
    from oops import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_config_manager_init():
    """测试配置管理器初始化"""
    from oops.core.config import ConfigManager

    config_manager = ConfigManager()
    assert config_manager is not None
    assert hasattr(config_manager, "config_dir")
    assert hasattr(config_manager, "master_config")
    assert hasattr(config_manager, "project_configs")


def test_default_config_loader_init():
    """测试默认配置加载器初始化"""
    from oops.core.default_config import DefaultConfigLoader

    loader = DefaultConfigLoader()
    assert loader is not None
    assert hasattr(loader, "config_dir")
    assert hasattr(loader, "defaults_file")


def test_default_config_loader_load():
    """测试加载默认配置"""
    from oops.core.default_config import DefaultConfigLoader

    loader = DefaultConfigLoader()
    defaults = loader.load_defaults()

    assert defaults is not None
    assert isinstance(defaults, dict)


def test_network_defaults():
    """测试网络默认配置"""
    from oops.core.default_config import DefaultConfigLoader

    loader = DefaultConfigLoader()
    network_defaults = loader.get_network_defaults()

    assert network_defaults is not None
    assert isinstance(network_defaults, dict)


def test_diagnostic_suite_init():
    """测试诊断套件初始化"""
    from oops.core.diagnostics import DiagnosticSuite

    suite = DiagnosticSuite()
    assert suite is not None
    assert hasattr(suite, "detectors")


def test_report_generator_init():
    """测试报告生成器初始化"""
    from oops.core.report import ReportGenerator

    generator = ReportGenerator()
    assert generator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
