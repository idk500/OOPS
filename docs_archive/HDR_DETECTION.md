# HDR 和显示设置检测

## 功能说明

OOPS 现在可以自动检测 Windows 系统的显示设置，包括：

### 检测项目

1. **HDR（高动态范围）**
2. **夜间模式/护眼模式**
3. **颜色滤镜**
4. **NVIDIA 游戏滤镜**（进程检测）

所有显示设置在报告中单独分类显示，便于查看。

### 1. HDR（高动态范围）检测

**为什么需要检测 HDR？**
- HDR 会改变屏幕的色彩和亮度范围
- 这会影响游戏脚本的图像识别准确性
- 可能导致脚本无法正确识别游戏界面元素

**检测方法**：
- 读取 Windows 注册表中的 HDR 设置
- 路径：`HKCU:\Software\Microsoft\Windows\CurrentVersion\VideoSettings`
- 键值：`EnableHDR`（1=启用，0=禁用）

**检测结果**：
```
显示设置: ❌ 检测到可能影响识别的显示设置
  问题: HDR已启用
  💡 关闭HDR以避免影响游戏脚本的图像识别
```

### 2. 夜间模式/护眼模式检测

**为什么需要检测？**
- 夜间模式会改变屏幕色温（偏暖色）
- 色温变化会影响颜色识别
- 可能导致基于颜色的识别失败

**检测方法**：
- 读取 Windows 注册表中的夜间模式设置
- 路径：`HKCU:\Software\Microsoft\Windows\CurrentVersion\CloudStore\...\bluelightreductionstate`

**检测结果**：
```
显示设置: ⚠️ 检测到可能影响识别的显示设置（警告）
  问题: 夜间模式/护眼模式已启用
  💡 关闭夜间模式以避免色温变化影响识别
```

### 3. 颜色滤镜检测

**为什么需要检测？**
- 颜色滤镜会改变屏幕颜色显示
- 可能用于色盲辅助或其他用途
- 会严重影响颜色识别准确性

**检测方法**：
- 读取 Windows 注册表中的颜色滤镜设置
- 路径：`HKCU:\Software\Microsoft\ColorFiltering`

**检测结果**：
```
显示设置: ❌ 检测到可能影响识别的显示设置
  问题: 颜色滤镜已启用
  💡 关闭颜色滤镜以避免颜色失真影响识别
```

### 4. NVIDIA 游戏滤镜检测

**为什么需要检测？**
- NVIDIA 游戏滤镜可以实时调整游戏画面
- 包括锐化、色彩增强、HDR 等效果
- 会改变游戏画面的像素值，影响识别

**检测方法**：
- 检测 NVIDIA 相关进程（GeForce Experience、Overlay）
- 注意：这只是进程检测，不能100%确定滤镜是否启用

**检测结果**：
```
显示设置: ⚠️ 检测到可能影响识别的显示设置（警告）
  问题: 可能启用了NVIDIA游戏滤镜
  💡 如果使用了NVIDIA游戏滤镜，建议关闭以避免影响识别
```

## 如何关闭这些设置

### 关闭 HDR

**Windows 11**：
1. 打开"设置" → "系统" → "显示器"
2. 找到"HDR"部分
3. 关闭"使用 HDR"开关

**Windows 10**：
1. 打开"设置" → "系统" → "显示"
2. 找到"Windows HD Color 设置"
3. 关闭"播放 HDR 游戏和应用"

### 关闭夜间模式

**Windows 11/10**：
1. 打开"设置" → "系统" → "显示器"
2. 找到"夜间模式"
3. 关闭夜间模式开关

或者：
1. 点击任务栏右下角的通知图标
2. 找到"夜间模式"快捷按钮
3. 点击关闭

## 技术实现

### PowerShell 检测脚本

```powershell
# 检测 HDR
$hdrKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\VideoSettings'
if (Test-Path $hdrKey) {
    $hdrValue = Get-ItemProperty -Path $hdrKey -Name 'EnableHDR' -ErrorAction SilentlyContinue
    if ($hdrValue) {
        $hdrValue.EnableHDR  # 1=启用, 0=禁用
    }
}

# 检测夜间模式
$nightLightKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\CloudStore\...'
if (Test-Path $nightLightKey) {
    $value = Get-ItemProperty -Path $nightLightKey -Name 'Data' -ErrorAction SilentlyContinue
    if ($value -and $value.Data.Length -gt 18) {
        $value.Data[18] -eq 0x15  # True=启用, False=禁用
    }
}
```

### Python 实现

```python
# oops/detectors/system_info.py
class SystemInfoDetector:
    def _check_hdr_status(self) -> Optional[bool]:
        """检测 Windows HDR 状态"""
        # 使用 PowerShell 读取注册表
        # 返回 True/False/None
        
    def _check_night_light(self) -> Optional[bool]:
        """检测 Windows 夜间模式状态"""
        # 使用 PowerShell 读取注册表
        # 返回 True/False/None
    
    def _validate_display_settings(self, basic_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """验证显示设置"""
        # HDR 启用 → 错误级别
        # 夜间模式启用 → 警告级别
```

## 报告显示

### 系统信息 - 显示设置分类

```
【显示设置】
  HDR: False ✅
  夜间模式/护眼模式: False ✅
  颜色滤镜: False ✅
  NVIDIA游戏滤镜: None ❓
```

### 硬件验证 - 显示设置验证

**无问题时**：
不显示显示设置验证（因为没有问题）

**有问题时**：
```
【硬件验证】
  内存验证: ✅ 内存充足: 15.9GB
  磁盘类型: ⚠️ 使用机械硬盘(HDD)可能会发生运行异常
    💡 强烈建议使用固态硬盘(SSD)
  显示设置: ❌ 检测到可能影响识别的显示设置
    问题: HDR已启用; 颜色滤镜已启用
    💡 关闭HDR以避免影响游戏脚本的图像识别
    💡 关闭颜色滤镜以避免颜色失真影响识别
```

## 兼容性

- ✅ Windows 10（1903 及以上）
- ✅ Windows 11
- ❌ Windows 7/8（不支持 HDR）
- ❌ Linux/macOS（暂不支持）

## 注意事项

1. **权限要求**：读取注册表不需要管理员权限
2. **检测失败**：如果检测失败，返回 `None`，不影响其他检测
3. **性能影响**：检测过程很快（< 1秒），不影响整体性能
4. **隐私保护**：只读取显示设置，不收集其他信息

## 报告优化

### 默认隐藏成功项

所有检测项现在默认隐藏成功详情，只展开失败和警告项：

```
environment_dependencies
❌ 失败项:
  virtual_environment: 未在虚拟环境中运行

[▶ 显示通过项 (3)]  ← 点击展开查看成功项
```

这样可以：
- ✅ 聚焦问题，快速定位需要修复的项
- ✅ 减少信息噪音，提高可读性
- ✅ 保留完整信息，需要时可以展开查看

## 未来扩展

可能添加的检测项：
- [ ] 显示器刷新率
- [ ] 显示缩放比例（DPI）
- [ ] 色彩配置文件
- [ ] 游戏模式状态
- [ ] 硬件加速状态
- [ ] AMD FreeSync / NVIDIA G-Sync
- [ ] 显示器 ICC 配置文件

## 参考资料

- [Windows HDR 设置文档](https://support.microsoft.com/zh-cn/windows/windows-hdr)
- [夜间模式设置](https://support.microsoft.com/zh-cn/windows/night-light)
- [Windows 注册表结构](https://docs.microsoft.com/zh-cn/windows/win32/sysinfo/registry)
