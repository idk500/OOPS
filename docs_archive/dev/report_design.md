# OOPS 报告系统设计

## 🎯 设计目标

基于Round 4审批意见，设计清晰、用户友好的报告输出系统，支持控制台实时输出和文件报告双重输出。

## 📋 报告格式设计

### 1. 报告格式优先级
- **主要格式**: Markdown (.md) - 人类可读，支持emoji和格式
- **备用格式**: YAML (.yaml) - 机器可读，便于程序处理
- **TBD格式**: HTML、JSON - 后续版本考虑

### 2. 报告文件命名
```
oops_report_{timestamp}.md
oops_report_{timestamp}.yaml

示例:
oops_report_20241119_164830.md
oops_report_20241119_164830.yaml
```

## 🎨 显眼标记系统

### 1. 状态标记
- ✅ **通过** (PASS) - 检测通过
- ❌ **失败** (FAIL) - 检测失败
- ⚠️ **警告** (WARN) - 需要注意但不影响运行
- ℹ️ **信息** (INFO) - 一般信息
- 🔧 **修复** (FIX) - 已自动修复的问题

### 2. 颜色编码 (控制台输出)
```python
# 控制台颜色编码
COLORS = {
    "PASS": "\033[92m",  # 绿色
    "FAIL": "\033[91m",  # 红色  
    "WARN": "\033[93m",  # 黄色
    "INFO": "\033[94m",  # 蓝色
    "FIX": "\033[96m",   # 青色
    "RESET": "\033[0m"   # 重置
}
```

## 📊 报告结构设计

### 1. Markdown报告结构
```markdown
# OOPS 检测报告

## 📅 报告信息
- **检测时间**: 2024-11-19 16:48:30
- **项目类型**: OneDragon
- **检测路径**: D:\Projects\ZenlessZoneZero-OneDragon
- **总体状态**: ✅ 通过 / ❌ 失败

## 🚨 问题摘要
| 模块 | 状态 | 问题数量 | 修复建议 |
|------|------|----------|----------|
| 硬件配置 | ✅ | 0 | - |
| 网络连通性 | ⚠️ | 1 | 检查GitHub连接 |
| 环境依赖 | ❌ | 2 | 修复Python环境 |

## 📋 详细检测结果

### 1. 🖥️ 硬件配置检测
✅ **CPU兼容性**: Intel Core i7-12700H (第12代)
✅ **内存容量**: 16GB (满足最低8GB要求)
✅ **GPU能力**: NVIDIA RTX 3060 (6GB VRAM)
⚠️ **存储类型**: HDD (建议使用SSD提升性能)

### 2. 🌐 网络连通性检测
✅ **GitHub主仓库**: 连接正常 (响应时间: 120ms)
❌ **GitHub镜像**: 连接超时 (建议使用Gitee镜像)
✅ **PyPI官方源**: 连接正常
✅ **PyPI清华源**: 连接正常

### 3. 🐍 环境依赖检测
✅ **Python版本**: 3.9.13 (兼容)
❌ **虚拟环境**: 未找到虚拟环境 (建议创建venv)
🔧 **依赖包**: 自动修复了缺失的pyautogui包

## 💡 修复建议

### 立即修复 (高优先级)
1. **创建虚拟环境**: 运行 `python -m venv .venv`
2. **切换Git镜像**: 在配置中使用Gitee镜像源

### 优化建议 (中优先级)  
1. **升级存储**: 考虑使用SSD提升项目启动速度
2. **网络代理**: 如有网络问题可配置代理

### 信息提示 (低优先级)
1. **硬件兼容**: 当前配置满足项目要求

## 🔗 相关资源
- [项目文档](https://one-dragon.com)
- [问题反馈](https://github.com/idk500/OOPS/issues)
- [使用指南](https://one-dragon.com/docs)

---
*报告生成时间: 2024-11-19 16:48:30 | OOPS v1.0*
```

### 2. YAML报告结构
```yaml
report_info:
  timestamp: "2024-11-19 16:48:30"
  project_type: "OneDragon"
  detection_path: "D:\Projects\ZenlessZoneZero-OneDragon"
  overall_status: "FAIL"

summary:
  total_checks: 15
  passed: 12
  failed: 2
  warnings: 1
  fixed: 1

modules:
  hardware:
    status: "PASS"
    checks:
      - name: "CPU Compatibility"
        status: "PASS"
        details: "Intel Core i7-12700H (12th Gen)"
      - name: "Memory Capacity" 
        status: "PASS"
        details: "16GB (meets 8GB minimum)"
      - name: "GPU Capability"
        status: "PASS"
        details: "NVIDIA RTX 3060 (6GB VRAM)"
      - name: "Storage Type"
        status: "WARN"
        details: "HDD (SSD recommended for better performance)"

  network:
    status: "WARN"
    checks:
      - name: "GitHub Main"
        status: "PASS"
        response_time: 120
      - name: "GitHub Mirror"
        status: "FAIL"
        error: "Connection timeout"
        suggestion: "Use Gitee mirror"

  environment:
    status: "FAIL"
    checks:
      - name: "Python Version"
        status: "PASS"
        version: "3.9.13"
      - name: "Virtual Environment"
        status: "FAIL"
        error: "Virtual environment not found"
        fix: "python -m venv .venv"
      - name: "Dependencies"
        status: "FIX"
        action: "auto_install_pyautogui"

recommendations:
  high_priority:
    - "Create virtual environment: python -m venv .venv"
    - "Switch to Gitee mirror for better connectivity"
  
  medium_priority:
    - "Consider upgrading to SSD for better performance"
    - "Configure network proxy if needed"

  low_priority:
    - "Hardware configuration meets project requirements"
```

## 🖥️ 控制台实时输出设计

### 1. 运行过程输出
```
🔍 OOPS 检测启动中...
📁 检测路径: D:\Projects\ZenlessZoneZero-OneDragon
🎯 项目类型: OneDragon (自动识别)

🖥️ 硬件配置检测...
  ✅ CPU: Intel Core i7-12700H (12th Gen)
  ✅ 内存: 16GB 
  ✅ GPU: NVIDIA RTX 3060
  ⚠️ 存储: HDD (建议使用SSD)

🌐 网络连通性检测...
  ✅ GitHub: 连接正常 (120ms)
  ❌ GitHub镜像: 连接超时
  ✅ PyPI官方源: 连接正常

🐍 环境依赖检测...
  ✅ Python: 3.9.13
  ❌ 虚拟环境: 未找到
  🔧 依赖包: 自动修复pyautogui

📊 检测完成!
📄 报告已保存: oops_report_20241119_164830.md
💡 提示: 查看报告文件获取详细修复建议
```

### 2. 状态指示器
```python
def print_status(module, check, status, details=""):
    """打印带颜色的状态信息"""
    colors = {
        "PASS": "✅",
        "FAIL": "❌", 
        "WARN": "⚠️",
        "FIX": "🔧",
        "INFO": "ℹ️"
    }
    print(f"  {colors[status]} {check}: {details}")
```

## 🔧 实现方案

### 1. 报告生成器类
```python
class ReportGenerator:
    def __init__(self, project_type, detection_path):
        self.project_type = project_type
        self.detection_path = detection_path
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
    
    def add_result(self, module, check, status, details):
        """添加检测结果"""
        if module not in self.results:
            self.results[module] = []
        self.results[module].append({
            "check": check,
            "status": status,
            "details": details
        })
    
    def generate_markdown(self):
        """生成Markdown报告"""
        # 实现Markdown模板填充
        pass
    
    def generate_yaml(self):
        """生成YAML报告"""
        # 实现YAML格式输出
        pass
    
    def print_console_summary(self):
        """控制台实时输出摘要"""
        # 实现控制台输出
        pass
```

### 2. 用户引导
- **运行结束提示**: 明确显示报告文件位置
- **文件位置**: 与oops.exe同目录或项目根目录
- **打开方式**: 提示用户可用文本编辑器打开查看

## 🚀 实施计划

### Phase 1: 基础报告系统 (Week 1)
- Markdown报告模板实现
- 控制台实时输出
- 基础状态标记系统

### Phase 2: 格式完善 (Week 2)
- YAML报告格式实现
- 颜色编码控制台输出
- 报告文件自动命名

### Phase 3: 高级功能 (Week 3+)
- HTML可视化报告
- JSON格式导出
- 报告比较功能

这个设计确保了用户能够快速理解检测结果，并通过显眼的标记和颜色编码快速定位问题。