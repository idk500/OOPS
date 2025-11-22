# OOPS 图标指南

## 图标文件

OOPS 项目包含以下图标文件：

- `oops.png` - 原始 PNG 格式图标
- `oops.ico` - Windows ICO 格式图标（用于 exe 文件）

## 图标规格

### PNG 图标
- 格式：PNG
- 用途：项目展示、文档、网页等

### ICO 图标
- 格式：ICO（Windows 图标）
- 包含尺寸：
  - 16x16 - 小图标（任务栏、文件列表）
  - 32x32 - 标准图标（桌面、文件夹）
  - 48x48 - 大图标（详细视图）
  - 64x64 - 超大图标
  - 128x128 - 高清图标
  - 256x256 - 超高清图标（Windows 7+）

## 如何更新图标

### 1. 准备新图标

确保你的图标：
- 格式：PNG
- 建议尺寸：256x256 或更大
- 背景：透明（RGBA）
- 风格：简洁、清晰、易识别

### 2. 转换为 ICO 格式

使用 Python 脚本转换：

```python
from PIL import Image

def convert_png_to_ico(png_path: str, ico_path: str):
    """转换 PNG 到 ICO"""
    img = Image.open(png_path)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"✅ 转换完成: {ico_path}")

# 使用
convert_png_to_ico('oops.png', 'oops.ico')
```

**依赖**：
```bash
pip install Pillow
```

### 3. 更新构建配置

图标已配置在 `build/config/build.spec` 中：

```python
exe = EXE(
    ...
    icon='oops.ico',  # OOPS 图标
    ...
)
```

### 4. 重新构建

运行构建脚本：

```bash
# Windows
build\scripts\build.bat

# Linux/macOS
chmod +x build/scripts/build.sh
build/scripts/build.sh
```

## 在线工具

如果不想使用 Python，可以使用在线工具：

1. **ConvertICO** - https://convertico.com/
   - 上传 PNG
   - 选择多个尺寸
   - 下载 ICO

2. **ICO Convert** - https://icoconvert.com/
   - 支持批量转换
   - 自定义尺寸

3. **Favicon Generator** - https://realfavicongenerator.net/
   - 生成多平台图标
   - 包括 ICO、PNG、SVG

## 图标设计建议

### 视觉元素
- ✅ 简洁明了
- ✅ 高对比度
- ✅ 易于识别
- ❌ 避免过多细节
- ❌ 避免小字体

### 颜色
- 使用品牌色
- 确保在深色/浅色背景下都清晰
- 考虑色盲友好

### 测试
在不同尺寸下测试：
- 16x16 - 是否仍然清晰？
- 32x32 - 主要元素是否可见？
- 256x256 - 细节是否合适？

## 故障排除

### 图标未显示

1. **检查文件路径**
   ```python
   # build.spec 中的路径应该相对于项目根目录
   icon='oops.ico'  # ✅ 正确
   icon='build/oops.ico'  # ❌ 错误（如果文件在根目录）
   ```

2. **检查文件格式**
   ```bash
   # 确认是 ICO 格式
   file oops.ico
   # 输出应该包含 "MS Windows icon"
   ```

3. **重新构建**
   ```bash
   # 清理旧文件
   rm -rf build dist
   
   # 重新构建
   pyinstaller --clean build/config/build.spec
   ```

### 图标模糊

- 确保 ICO 包含多个尺寸
- 使用矢量图作为源（SVG）
- 在小尺寸下简化设计

### 构建失败

```
Error: Unable to find icon file
```

**解决方案**：
1. 确认 `oops.ico` 在项目根目录
2. 检查 `build.spec` 中的路径
3. 使用绝对路径测试：`icon='C:/path/to/oops.ico'`

## 参考资料

- [PyInstaller 图标文档](https://pyinstaller.org/en/stable/usage.html#cmdoption-i)
- [Windows 图标规范](https://docs.microsoft.com/en-us/windows/win32/uxguide/vis-icons)
- [Pillow 文档](https://pillow.readthedocs.io/)
