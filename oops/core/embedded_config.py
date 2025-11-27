"""
嵌入式配置管理模块
负责加载和管理嵌入式配置文件
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class EmbeddedConfigLoader:
    """嵌入式配置加载器"""

    def __init__(self):
        # 获取嵌入式配置目录路径
        self.embedded_config_dir = Path(__file__).parent.parent / "configs_embedded"
        self.external_config_dir = Path("configs")
        
    def load_config(self, config_name: str, use_external_first: bool = True) -> Optional[Dict[str, Any]]:
        """加载配置文件
        
        Args:
            config_name: 配置文件名（不含扩展名）
            use_external_first: 是否优先使用外部配置
            
        Returns:
            配置字典，如果加载失败则返回None
        """
        config_path = f"{config_name}.yaml"
        
        # 优先检查外部配置
        if use_external_first:
            external_path = self.external_config_dir / config_path
            if external_path.exists():
                try:
                    with open(external_path, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f)
                    logger.info(f"已加载外部配置: {external_path}")
                    return config
                except Exception as e:
                    logger.warning(f"加载外部配置失败: {e}，尝试使用嵌入式配置")
        
        # 检查嵌入式配置
        embedded_path = self.embedded_config_dir / config_path
        if embedded_path.exists():
            try:
                with open(embedded_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                logger.info(f"已加载嵌入式配置: {embedded_path}")
                return config
            except Exception as e:
                logger.error(f"加载嵌入式配置失败: {e}")
                return None
        
        logger.warning(f"配置文件不存在: {config_path}")
        return None
    
    def load_master_config(self, use_external_first: bool = True) -> Optional[Dict[str, Any]]:
        """加载主配置文件"""
        return self.load_config("oops_master", use_external_first)
    
    def load_project_config(self, project_name: str, use_external_first: bool = True) -> Optional[Dict[str, Any]]:
        """加载项目配置文件"""
        return self.load_config(project_name, use_external_first)
    
    def load_defaults_config(self, use_external_first: bool = True) -> Optional[Dict[str, Any]]:
        """加载默认配置文件"""
        return self.load_config("defaults", use_external_first)
    
    def get_config_path(self, config_name: str, use_external_first: bool = True) -> Optional[Path]:
        """获取配置文件路径
        
        Args:
            config_name: 配置文件名（不含扩展名）
            use_external_first: 是否优先返回外部配置路径
            
        Returns:
            配置文件路径，如果不存在则返回None
        """
        config_path = f"{config_name}.yaml"
        
        if use_external_first:
            external_path = self.external_config_dir / config_path
            if external_path.exists():
                return external_path
        
        embedded_path = self.embedded_config_dir / config_path
        if embedded_path.exists():
            return embedded_path
        
        return None
    
    def is_external_config_available(self, config_name: str) -> bool:
        """检查外部配置是否可用"""
        config_path = f"{config_name}.yaml"
        external_path = self.external_config_dir / config_path
        return external_path.exists()
