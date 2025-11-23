# 网络检测器架构重构计划

## 📋 背景

当前网络检测器的实现存在架构问题：具体的URL硬编码在项目配置中，而网络检测器应该只提供抽象的通路检测方法。

## 🎯 重构目标

将网络检测器重构为抽象的连通性检测方法，具体的URL配置分离到默认配置和项目配置中。

## 📊 当前架构问题

### 问题1：URL硬编码在项目配置中

**当前实现**：
```yaml
# configs/zenless_zone_zero.yaml
checks:
  network:
    git_repos:
      - https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git
    pypi_sources:
      - https://pypi.org/simple/
      - https://pypi.tuna.tsinghua.edu.cn/simple/
```

**问题**：
- 每个项目都要配置相同的PyPI源
- 默认的测试URL分散在各个项目配置中
- 无法统一管理常用的测试目标
- 新项目需要重复配置

### 问题2：检测器不够抽象

**当前实现**：
- 网络检测器直接处理具体的URL
- 检测逻辑和配置数据混在一起
- 难以扩展新的检测类型

## 🏗️ 理想架构

### 架构层次

```
┌─────────────────────────────────────┐
│   网络检测器 (抽象方法)              │
│   - HTTP连通性检测                   │
│   - Git连通性检测                    │
│   - PyPI源检测                       │
│   - UDP连通性检测                    │
└─────────────────────────────────────┘
              ↓ 使用
┌─────────────────────────────────────┐
│   默认配置 (defaults.yaml)           │
│   - 默认Git仓库列表                  │
│   - 默认PyPI源列表                   │
│   - 默认HTTP测试URL                  │
│   - 默认镜像站点                     │
└─────────────────────────────────────┘
              ↓ 可被覆盖
┌─────────────────────────────────────┐
│   项目配置 (zenless_zone_zero.yaml)  │
│   - 项目特定的Git仓库                │
│   - 项目特定的测试URL（可选）        │
└─────────────────────────────────────┘
```

### 配置文件结构

#### 1. 默认配置文件 `configs/defaults.yaml`

```yaml
# 默认网络检测配置
network_defaults:
  # Git仓库连通性测试
  git_repos:
    - url: https://github.com
      name: GitHub主站
      type: git_repo
    - url: https://gitee.com
      name: Gitee
      type: git_repo
  
  # PyPI源测试
  pypi_sources:
    - url: https://pypi.org/simple/
      name: PyPI官方源
      type: pypi_source
    - url: https://pypi.tuna.tsinghua.edu.cn/simple/
      name: 清华大学镜像
      type: pypi_source
    - url: https://mirrors.aliyun.com/pypi/simple/
      name: 阿里云镜像
      type: pypi_source
  
  # 镜像站点测试
  mirror_sites:
    - url: https://mirrors.tuna.tsinghua.edu.cn
      name: 清华大学开源镜像站
      type: mirror_site
    - url: https://mirrors.aliyun.com
      name: 阿里云镜像站
      type: mirror_site
  
  # HTTP连通性测试
  http_endpoints:
    - url: https://www.baidu.com
      name: 百度
      type: http_test
    - url: https://www.google.com
      name: Google
      type: http_test
```

#### 2. 项目配置文件 `configs/zenless_zone_zero.yaml`

```yaml
project:
  name: 绝区零一条龙
  type: game_script
  description: 绝区零自动化脚本

checks:
  network:
    enabled: true
    # 项目特定的Git仓库（会添加到默认列表）
    git_repos:
      - url: https://github.com/OneDragon-Anything/ZenlessZoneZero-OneDragon.git
        name: 绝区零一条龙项目
        type: git_repo
    
    # 可选：覆盖默认的PyPI源（如果不指定，使用默认配置）
    # pypi_sources: []
    
    # 可选：禁用某些默认检测
    # disable_defaults:
    #   - http_endpoints
```

### 配置合并逻辑

```python
# 伪代码
def get_network_config(project_config):
    # 1. 加载默认配置
    defaults = load_defaults()
    
    # 2. 获取项目配置
    project_network = project_config.get('checks', {}).get('network', {})
    
    # 3. 合并配置
    final_config = {
        'git_repos': defaults['git_repos'] + project_network.get('git_repos', []),
        'pypi_sources': project_network.get('pypi_sources', defaults['pypi_sources']),
        'mirror_sites': defaults['mirror_sites'],
        'http_endpoints': defaults['http_endpoints']
    }
    
    # 4. 处理禁用项
    disable_list = project_network.get('disable_defaults', [])
    for item in disable_list:
        final_config.pop(item, None)
    
    return final_config
```

## 🔧 实施步骤

### 阶段1：创建默认配置系统 ✅

- [x] 创建 `configs/defaults.yaml` 文件
- [x] 定义默认的网络检测目标
- [x] 实现配置加载器 `DefaultConfigLoader`
- [x] 添加配置验证逻辑

### 阶段2：重构网络检测器 ✅

- [x] 修改 `NetworkDetector` 为抽象检测方法
- [x] 实现配置合并逻辑
- [x] 支持项目配置覆盖默认配置
- [x] 支持禁用默认检测项

### 阶段3：更新项目配置 ✅

- [x] 简化 `zenless_zone_zero.yaml` 配置
- [x] 简化 `generic_python.yaml` 配置
- [x] 只保留项目特定的URL
- [x] 移除重复的默认配置

### 阶段4：测试和文档 ✅

- [x] 测试配置合并逻辑
- [x] 测试配置覆盖功能
- [x] 更新用户文档
- [x] 更新开发文档

## 📝 实现细节

### 1. DefaultConfigLoader 类

```python
# oops/core/default_config.py

import yaml
from pathlib import Path
from typing import Dict, Any

class DefaultConfigLoader:
    """默认配置加载器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.defaults_file = self.config_dir / "defaults.yaml"
        self._defaults = None
    
    def load_defaults(self) -> Dict[str, Any]:
        """加载默认配置"""
        if self._defaults is None:
            if self.defaults_file.exists():
                with open(self.defaults_file, 'r', encoding='utf-8') as f:
                    self._defaults = yaml.safe_load(f)
            else:
                self._defaults = self._create_default_config()
        return self._defaults
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置（如果文件不存在）"""
        return {
            'network_defaults': {
                'git_repos': [
                    {'url': 'https://github.com', 'name': 'GitHub', 'type': 'git_repo'}
                ],
                'pypi_sources': [
                    {'url': 'https://pypi.org/simple/', 'name': 'PyPI官方', 'type': 'pypi_source'},
                    {'url': 'https://pypi.tuna.tsinghua.edu.cn/simple/', 'name': '清华镜像', 'type': 'pypi_source'}
                ]
            }
        }
    
    def get_network_defaults(self) -> Dict[str, Any]:
        """获取网络检测默认配置"""
        defaults = self.load_defaults()
        return defaults.get('network_defaults', {})
    
    def merge_with_project_config(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和项目配置"""
        defaults = self.get_network_defaults()
        project_network = project_config.get('checks', {}).get('network', {})
        
        # 合并逻辑
        merged = {}
        
        # Git仓库：追加项目特定的仓库
        merged['git_repos'] = (
            defaults.get('git_repos', []) + 
            project_network.get('git_repos', [])
        )
        
        # PyPI源：项目配置优先，否则使用默认
        merged['pypi_sources'] = (
            project_network.get('pypi_sources') or 
            defaults.get('pypi_sources', [])
        )
        
        # 其他配置项...
        for key in ['mirror_sites', 'http_endpoints', 'github_proxy', 'project_websites']:
            merged[key] = (
                project_network.get(key) or 
                defaults.get(key, [])
            )
        
        # 处理禁用项
        disable_list = project_network.get('disable_defaults', [])
        for item in disable_list:
            merged.pop(item, None)
        
        return merged
```

### 2. 修改 NetworkDetector

```python
# oops/detectors/network.py

from oops.core.default_config import DefaultConfigLoader

class NetworkDetector(DetectionRule):
    """网络连通性检测器 - 抽象检测方法"""
    
    def __init__(self):
        super().__init__(
            name="network_connectivity",
            description="网络连通性检测",
            severity="info",
        )
        self.timeout = 10
        self.default_loader = DefaultConfigLoader()
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """执行网络连通性检测"""
        try:
            # 合并默认配置和项目配置
            network_config = self.default_loader.merge_with_project_config(config)
            
            # 执行检测
            results = {}
            
            # 检测Git仓库
            for repo in network_config.get('git_repos', []):
                url = repo['url']
                results[url] = self._check_git_connectivity(url, repo.get('name'))
            
            # 检测PyPI源
            for source in network_config.get('pypi_sources', []):
                url = source['url']
                results[url] = self._check_pypi_source(url, source.get('name'))
            
            # ... 其他检测
            
            return {
                "status": "success",
                "message": f"网络检测完成，共检测 {len(results)} 个目标",
                "details": results
            }
        except Exception as e:
            logger.error(f"网络检测失败: {e}")
            return {"status": "error", "message": f"网络检测失败: {str(e)}"}
```

## 🎯 预期效果

### 优势

1. **配置复用**：默认配置可被所有项目使用
2. **易于维护**：统一管理常用的测试目标
3. **灵活性**：项目可以覆盖或扩展默认配置
4. **可扩展**：容易添加新的检测类型
5. **清晰分离**：检测逻辑和配置数据分离

### 用户体验

**新项目配置**：
```yaml
# 只需要配置项目特定的内容
project:
  name: 我的项目
  
checks:
  network:
    enabled: true
    git_repos:
      - url: https://github.com/myuser/myproject.git
        name: 我的项目仓库
```

**默认行为**：
- 自动测试常用的PyPI源
- 自动测试GitHub连通性
- 自动测试常用镜像站

## 📚 相关文件

### 需要修改的文件

1. `oops/core/default_config.py` - 新建，默认配置加载器
2. `oops/detectors/network.py` - 修改，使用默认配置
3. `configs/defaults.yaml` - 新建，默认配置文件
4. `configs/zenless_zone_zero.yaml` - 简化，移除默认配置
5. `configs/generic_python.yaml` - 简化，移除默认配置
6. `oops/core/config.py` - 可能需要修改配置管理器

### 需要更新的文档

1. `README.md` - 更新配置说明
2. `USAGE.md` - 更新使用指南
3. `docs/CONFIGURATION.md` - 详细配置文档

## ⚠️ 注意事项

1. **向后兼容**：确保旧的配置格式仍然可用
2. **渐进式迁移**：可以先支持新格式，再逐步迁移旧配置
3. **测试覆盖**：确保配置合并逻辑有充分的测试
4. **文档同步**：代码变更后立即更新文档

## 🚀 开始重构

当准备开始重构时：

1. 创建新分支：`git checkout -b refactor/network-detector-abstraction`
2. 按照实施步骤逐步进行
3. 每个阶段完成后提交
4. 充分测试后合并到主分支

---

## ✅ 实施完成

**完成时间**: 2025-11-23  
**状态**: ✅ 已完成  

### 实施总结

1. **创建了默认配置系统**
   - `configs/defaults.yaml` - 包含所有默认网络检测目标
   - `oops/core/default_config.py` - 配置加载和合并逻辑

2. **重构了网络检测器**
   - 使用 `DefaultConfigLoader` 自动合并配置
   - 支持简单字符串和字典两种配置格式
   - 支持 `disable_defaults` 禁用默认配置

3. **简化了项目配置**
   - 绝区零配置只保留项目特定的 Git 仓库
   - 通用Python配置使用完全默认配置
   - 配置文件更简洁，易于维护

4. **测试验证**
   - 所有配置合并逻辑测试通过
   - 实际运行检测验证功能正常
   - 向后兼容旧配置格式

### 效果

- ✅ 配置复用：所有项目共享默认配置
- ✅ 易于维护：统一管理常用测试目标
- ✅ 灵活性：项目可以覆盖或扩展
- ✅ 向后兼容：旧配置仍然可用

---

**创建时间**: 2025-11-23  
**完成时间**: 2025-11-23  
**创建者**: AI Assistant  
**状态**: ✅ 已完成  
**优先级**: 中等（功能完整，架构已优化）
