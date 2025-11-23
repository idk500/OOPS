# 游戏设置检测分析

## 概述

本文档分析配置文件中 `game_settings` 部分的各项设置，评估其检测的可行性、必要性和实现状态。

## 配置项分析

### 1. 分辨率检测 (resolution) ✅ 已实现

```yaml
resolution:
  check: true
  recommended: '1920x1080'
  aspect_ratio: '16:9'
```

#### 重要性: ⭐⭐⭐⭐⭐ (极高)
- 直接影响图像识别准确性
- 分辨率过低会导致UI元素无法识别
- 影响OCR文字识别效果

#### 可检测性: ⭐⭐⭐⭐⭐ (极高)
- Windows: System.Windows.Forms API
- Linux: xrandr 命令
- macOS: system_profiler 命令

#### 实现状态: ✅ 已完成
- 在 `system_info.py` 中实现
- 跨平台支持
- 自动验证是否满足最低要求
- 分辨率过低时显示错误级别警告

#### 验证逻辑
```python
if width < 1920 or height < 1080:
    return {'valid': False, 'severity': 'error'}
else:
    return {'valid': True, 'severity': 'info'}
```

---

### 2. 显示模式检测 (display_mode) ⚠️ 部分可行

```yaml
display_mode:
  check: true
  recommended: 'windowed'  # 或 'fullscreen'
```

#### 重要性: ⭐⭐⭐ (中等)
- 影响窗口捕获方式
- 全屏模式可能影响脚本的窗口操作
- 窗口模式更容易进行自动化控制

#### 可检测性: ⭐⭐ (较低)
**方法1: 检测游戏窗口状态**
- 需要游戏正在运行
- 可以通过 Windows API 检测窗口样式
- 但无法在游戏未运行时检测

**方法2: 读取游戏配置文件**
- 需要知道配置文件位置和格式
- 不同游戏配置文件格式不同
- 可能需要解析 JSON/INI/XML 等格式

#### 实现建议: 📝 提示性检查
```python
def check_display_mode(config):
    recommended = config.get('recommended', 'windowed')
    return {
        'status': 'info',
        'message': f'请确保游戏运行在 {recommended} 模式',
        'auto_check': False  # 无法自动验证
    }
```

#### 为什么不自动检测？
1. **游戏未运行时无法检测**: 大多数情况下，检测时游戏未启动
2. **配置文件位置不确定**: 不同游戏配置文件位置不同
3. **配置格式多样**: 需要为每个游戏单独实现解析逻辑
4. **收益较低**: 用户可以在游戏内轻松调整

---

### 3. 图形设置检测 (graphics) ❌ 不建议实现

```yaml
graphics:
  check: false
  quality_preset: 'medium'
```

#### 重要性: ⭐ (较低)
- 主要影响游戏性能和流畅度
- 对图像识别影响较小
- 用户可根据自己硬件调整

#### 可检测性: ⭐ (很低)
- 需要读取游戏配置文件
- 配置项名称和格式因游戏而异
- 无法通过系统API获取

#### 实现建议: ❌ 不实现
**原因**:
1. **对脚本运行影响小**: 图形质量不影响UI识别
2. **检测成本高**: 需要为每个游戏单独实现
3. **用户自主性强**: 用户应根据硬件自行调整
4. **维护成本高**: 游戏更新可能改变配置格式

---

## 其他可能的游戏设置检测

### 4. 刷新率检测 (refresh_rate) 🔄 可考虑

```yaml
refresh_rate:
  check: true
  recommended: '60Hz'
```

#### 重要性: ⭐⭐ (较低)
- 影响游戏流畅度
- 对图像识别影响较小
- 主要影响用户体验

#### 可检测性: ⭐⭐⭐⭐ (较高)
- Windows: 可通过 WMI 或 PowerShell 获取
- Linux: xrandr 可以显示刷新率
- macOS: system_profiler 可以获取

#### 实现建议: 📝 可选功能
```python
def check_refresh_rate():
    # Windows PowerShell
    ps_command = """
    $monitor = Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBasicDisplayParams
    $monitor.RefreshRate
    """
    # 返回刷新率信息
```

---

### 5. 窗口缩放/DPI检测 (dpi_scaling) 🔄 可考虑

```yaml
dpi_scaling:
  check: true
  recommended: '100%'
```

#### 重要性: ⭐⭐⭐⭐ (高)
- **严重影响坐标定位**: DPI缩放会导致坐标偏移
- **影响图像识别**: 界面元素大小改变
- **Windows 10/11 常见问题**: 默认可能启用125%或150%缩放

#### 可检测性: ⭐⭐⭐⭐ (较高)
- Windows: 可通过注册表或 API 获取
- 可以检测系统级和应用级缩放

#### 实现建议: ✅ 强烈推荐实现
```python
def check_dpi_scaling():
    # Windows: 检查系统DPI设置
    ps_command = """
    Add-Type -AssemblyName System.Windows.Forms
    $dpi = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width / 
           [System.Windows.Forms.SystemInformation]::PrimaryMonitorSize.Width
    $scaling = [math]::Round($dpi * 100)
    Write-Output "$scaling%"
    """
    # 如果不是100%，显示警告
```

---

### 6. 多显示器检测 (multi_monitor) 🔄 可考虑

```yaml
multi_monitor:
  check: true
  warn_if_multiple: true
```

#### 重要性: ⭐⭐⭐ (中等)
- 可能影响窗口捕获
- 游戏可能在非主显示器运行
- 分辨率可能不一致

#### 可检测性: ⭐⭐⭐⭐⭐ (极高)
- 所有平台都可以轻松检测
- 可以获取每个显示器的详细信息

#### 实现建议: 📝 信息性检查
```python
def check_multi_monitor():
    # 检测显示器数量
    # 如果有多个显示器，提示用户确认游戏运行在哪个显示器
    return {
        'monitor_count': 2,
        'message': '检测到多个显示器，请确保游戏运行在主显示器'
    }
```

---

## 实现优先级

### 高优先级 (建议实现)
1. ✅ **分辨率检测** - 已实现
2. 🔄 **DPI缩放检测** - 强烈推荐，影响坐标定位

### 中优先级 (可选实现)
3. 🔄 **多显示器检测** - 信息性检查
4. 📝 **显示模式检测** - 提示性检查（无法自动验证）

### 低优先级 (暂不实现)
5. 🔄 **刷新率检测** - 影响较小
6. ❌ **图形设置检测** - 成本高，收益低

---

## 实现路线图

### 第一阶段 ✅ (已完成)
- [x] 分辨率检测
- [x] 跨平台支持
- [x] 验证逻辑
- [x] 报告显示

### 第二阶段 🔄 (计划中)
- [ ] DPI缩放检测
- [ ] 多显示器检测
- [ ] 显示模式提示

### 第三阶段 📝 (未来考虑)
- [ ] 刷新率检测
- [ ] 游戏配置文件读取框架
- [ ] 自定义检测规则

---

## 技术实现建议

### 1. 模块化设计
```python
class GameSettingsDetector:
    def check_resolution(self):
        """分辨率检测 - 已实现"""
        pass
    
    def check_dpi_scaling(self):
        """DPI缩放检测 - 待实现"""
        pass
    
    def check_multi_monitor(self):
        """多显示器检测 - 待实现"""
        pass
    
    def check_display_mode(self):
        """显示模式检测 - 提示性"""
        pass
```

### 2. 配置驱动
```yaml
game_settings:
  enabled: true
  checks:
    - name: resolution
      enabled: true
      auto_check: true
      severity: error
    - name: dpi_scaling
      enabled: true
      auto_check: true
      severity: warning
    - name: display_mode
      enabled: true
      auto_check: false  # 仅提示
      severity: info
```

### 3. 扩展性
- 支持自定义检测规则
- 支持游戏特定的配置文件解析
- 支持插件式检测器

---

## 总结

### 当前实现
- ✅ 分辨率检测已完成
- ✅ 跨平台支持
- ✅ 自动验证和报告

### 推荐下一步
1. **DPI缩放检测**: 对坐标定位影响大，强烈推荐实现
2. **多显示器检测**: 实现简单，可以提供有用信息
3. **显示模式检测**: 作为提示性检查，不强制验证

### 不推荐实现
- ❌ 图形设置检测: 成本高，收益低
- ❌ 游戏内设置自动调整: 风险高，可能破坏游戏配置

---

## 参考资料

- [分辨率检测文档](RESOLUTION_DETECTION.md)
- [HDR检测文档](../HDR_DETECTION.md)
- [系统架构文档](../ARCHITECTURE.md)
