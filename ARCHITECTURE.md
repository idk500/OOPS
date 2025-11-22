# OOPS 架构文档

**OOPS - One-click Operating Pre-check System (一键运行预检系统)**

> 让游戏脚本运行更顺畅 | Run Your Game Scripts Smoothly

## 架构概览

OOPS 采用了**执行器-报告器解耦**的架构设计，确保检测逻辑和报告生成相互独立。

```
┌─────────────────┐
│  检测执行器层   │  ← 负责执行检测，输出标准化结果
├─────────────────┤
│  诊断协调器层   │  ← 协调多个检测器，管理执行流程
├─────────────────┤
│  报告生成器层   │  ← 将标准化结果转换为多种格式
└─────────────────┘
```

## 1. 检测执行器层 (Detectors)

### 职责
- 执行具体的检测逻辑
- 输出**标准化的检测结果**
- 不关心结果如何展示

### 标准输出格式

所有检测器都遵循统一的输出格式：

```python
{
    'status': 'success' | 'error' | 'warning' | 'skipped',
    'message': '简短的状态描述',
    'details': {
        # 详细的检测数据，结构化存储
        'item_name': {
            'status': 'success' | 'error' | 'warning',
            'message': '具体信息',
            'data': {...}  # 可选的额外数据
        }
    }
}
```

### 示例：系统信息检测器

```python
# oops/detectors/system_info.py
class SystemInfoDetector:
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'success',
            'message': '系统信息收集完成',
            'details': {
                'basic': {...},      # 基本信息
                'hardware': {...},   # 硬件信息
                'storage': {...},    # 存储信息
                'validation': {...}  # 验证结果
            }
        }
```

### 示例：网络检测器

```python
# oops/detectors/network.py
class NetworkConnectivityDetector:
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'success',
            'message': '网络检测完成，共检测 15 个目标',
            'details': {
                'github.com': {
                    'status': 'success',
                    'message': '连接成功',
                    'response_time': 0.5
                },
                'pypi.org': {
                    'status': 'error',
                    'message': '连接超时',
                    'error': 'Timeout'
                }
            }
        }
```

## 2. 诊断协调器层 (DiagnosticSuite)

### 职责
- 管理多个检测器的执行
- 收集和汇总检测结果
- 生成检测摘要
- 不涉及报告格式化

### 核心类

```python
# oops/core/diagnostics.py
class DiagnosticSuite:
    """诊断套件 - 核心检测协调器"""
    
    async def run_diagnostics(self, project_name: str) -> List[CheckResult]:
        """运行诊断检测，返回标准化结果列表"""
        pass
    
    def get_summary(self) -> Dict[str, Any]:
        """获取检测摘要统计"""
        return {
            'total_checks': 4,
            'completed': 4,
            'failed': 0,
            'warning_issues': 1,
            'success_rate': 100.0
        }
```

### CheckResult 数据类

```python
@dataclass
class CheckResult:
    """标准化的检测结果"""
    check_name: str              # 检测名称
    status: CheckStatus          # 状态枚举
    severity: SeverityLevel      # 严重程度
    message: str                 # 简短消息
    details: Dict[str, Any]      # 详细数据
    fix_suggestion: str          # 修复建议
    execution_time: float        # 执行时间
    timestamp: datetime          # 时间戳
```

## 3. 报告生成器层 (Report Generators)

### 职责
- 接收标准化的检测结果
- 转换为用户友好的多种格式
- 支持模块化扩展

### 模块化设计

```python
# oops/core/report_modules.py
class ReportModule:
    """报告模块基类"""
    def generate_html(self, data: Any) -> str: pass
    def generate_json(self, data: Any) -> Dict: pass

class SystemInfoModule(ReportModule):
    """系统信息报告模块"""
    pass

class CheckResultsModule(ReportModule):
    """检测结果报告模块"""
    pass
```

### 支持的格式

1. **HTML报告** - 交互式网页报告
   - 折叠/展开功能
   - 彩色状态标识
   - 响应式布局

2. **JSON报告** - 机器可读格式
   - 完整的结构化数据
   - 便于程序处理

3. **Markdown报告** - 文本格式
   - 便于版本控制
   - 易于阅读和分享

### 报告生成流程

```python
# oops/core/report.py
class ReportGenerator:
    def generate_report(self, results: List[CheckResult], 
                       project_name: str, 
                       summary: Dict[str, Any]) -> str:
        """
        输入：标准化的检测结果
        输出：格式化的报告内容
        """
        if self.config.format == "html":
            return self._generate_html_report(results, project_name, summary)
        elif self.config.format == "json":
            return self._generate_json_report(results, project_name, summary)
        elif self.config.format == "markdown":
            return self._generate_markdown_report(results, project_name, summary)
```

## 架构优势

### 1. 解耦性
- **检测器**只关心检测逻辑，不关心如何展示
- **报告器**只关心格式化，不关心检测逻辑
- 两者通过标准化的数据结构通信

### 2. 可扩展性
- 新增检测器：只需实现 `check()` 方法，返回标准格式
- 新增报告格式：只需实现新的 `ReportModule`
- 互不影响

### 3. 可测试性
- 检测器可以独立测试
- 报告器可以用模拟数据测试
- 单元测试更容易编写

### 4. 可维护性
- 职责清晰，代码组织良好
- 修改检测逻辑不影响报告
- 修改报告样式不影响检测

## 数据流示例

```
1. 用户执行检测
   ↓
2. DiagnosticSuite 协调多个检测器
   ↓
3. 每个检测器返回标准化结果
   {
     'status': 'success',
     'message': '...',
     'details': {...}
   }
   ↓
4. DiagnosticSuite 收集所有结果
   List[CheckResult]
   ↓
5. ReportGenerator 接收结果
   ↓
6. ReportModuleManager 调用各个模块
   ↓
7. 生成最终报告
   - HTML: 交互式网页
   - JSON: 结构化数据
   - Markdown: 文本文档
```

## 开发者指南

### 添加新的检测器

```python
# oops/detectors/my_detector.py
class MyDetector(DetectionRule):
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # 执行检测逻辑
        result = self._do_check()
        
        # 返回标准格式
        return {
            'status': 'success',
            'message': '检测完成',
            'details': {
                'item1': {'status': 'success', 'message': '...'},
                'item2': {'status': 'error', 'message': '...'}
            }
        }
```

### 添加新的报告模块

```python
# oops/core/report_modules.py
class MyReportModule(ReportModule):
    def __init__(self):
        super().__init__("my_module", "📋 我的模块")
    
    def generate_html(self, data: Any) -> str:
        # 将数据转换为HTML
        return f"<div>...</div>"
    
    def generate_json(self, data: Any) -> Dict[str, Any]:
        # 将数据转换为JSON
        return {"module": self.name, "data": data}
```

## 总结

OOPS 的架构设计确保了：
- ✅ **执行器输出标准化结果** - 易于理解和处理
- ✅ **报告器独立于检测逻辑** - 灵活的格式化
- ✅ **模块化设计** - 易于扩展和维护
- ✅ **清晰的职责分离** - 代码组织良好

这种架构使得 OOPS 既能满足开发者快速理解检测结果的需求，又能为用户提供友好的多格式报告。
