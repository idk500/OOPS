# OOPS 构建指南

## 📦 构建单一可执行文件

OOPS 使用 PyInstaller 将 Python 代码打包成单一的可执行文件，无需安装 Python 环境即可运行。

---

## 🚀 快速构建

### Windows

```bash
# 方式1: 使用构建脚本（推荐）
build.bat

# 方式2: 手动构建
pip install pyinstaller
pyinstaller --clean --noconfirm build.spec
```

### Linux / macOS

```bash
# 方式1: 使用构建脚本（推荐）
chmod +x build.sh
./build.sh

# 方式2: 手动构建
pip install pyinstaller
pyinstaller --clean --noconfirm build.spec
```

---

## 📋 构建要求

### 系统要求
- **Windows**: Windows 10+ (64位)
- **Linux**: Ubuntu 18.04+ 或其他主流发行版
- **macOS**: macOS 10.13+

### 软件要求
- Python 3.8 或更高版本
- pip (Python包管理器)
- 所有项目依赖（见 requirements.txt）

---

## 🔧 构建配置

### build.spec 文件

PyInstaller 配置文件，控制构建行为：

```python
# 主要配置项
datas = [
    ('configs', 'configs'),              # 配置文件
    ('docs/knowledge_base', 'docs/knowledge_base'),  # 知识库
]

hiddenimports = [
    'oops.core.config',
    'oops.detectors.network',
    # ... 其他模块
]

excludes = [
    'matplotlib',  # 排除不需要的大型库
    'numpy',
    'pandas',
]
```

### 自定义配置

如需修改构建配置，编辑 `build.spec` 文件：

1. **添加数据文件**
   ```python
   datas = [
       ('your_data_dir', 'your_data_dir'),
   ]
   ```

2. **添加隐藏导入**
   ```python
   hiddenimports = [
       'your_module',
   ]
   ```

3. **添加图标**
   ```python
   icon='path/to/icon.ico'  # Windows
   icon='path/to/icon.icns'  # macOS
   ```

---

## 📊 构建输出

### 文件结构

```
dist/
└── oops.exe          # Windows可执行文件
    或
    oops              # Linux/macOS可执行文件
```

### 文件大小

- **Windows**: 约 30-50 MB
- **Linux**: 约 25-40 MB
- **macOS**: 约 30-45 MB

> 注意：文件大小取决于包含的依赖库数量

---

## 🧪 测试构建

### 基础测试

```bash
# Windows
dist\oops.exe --version
dist\oops.exe --help
dist\oops.exe --list-projects

# Linux/macOS
./dist/oops --version
./dist/oops --help
./dist/oops --list-projects
```

### 完整测试

```bash
# 1. 复制到测试目录
mkdir test_oops
cp dist/oops.exe test_oops/  # Windows
cp dist/oops test_oops/      # Linux/macOS

# 2. 运行测试
cd test_oops
./oops.exe  # Windows
./oops      # Linux/macOS
```

---

## 🔍 故障排除

### 问题1: 构建失败 - 缺少模块

**错误信息**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:
1. 安装缺失的模块: `pip install xxx`
2. 或在 `build.spec` 中添加到 `hiddenimports`

### 问题2: 运行时错误 - 找不到文件

**错误信息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'configs/...'
```

**解决方案**:
在 `build.spec` 中添加数据文件：
```python
datas = [
    ('configs', 'configs'),
]
```

### 问题3: 可执行文件过大

**解决方案**:
1. 在 `build.spec` 中排除不需要的库：
   ```python
   excludes = [
       'matplotlib',
       'numpy',
       'pandas',
   ]
   ```

2. 启用 UPX 压缩：
   ```python
   upx=True
   ```

3. 安装 UPX:
   - Windows: 下载 https://upx.github.io/
   - Linux: `sudo apt install upx`
   - macOS: `brew install upx`

### 问题4: 杀毒软件误报

**原因**: PyInstaller 打包的程序可能被误报为病毒

**解决方案**:
1. 添加到杀毒软件白名单
2. 使用代码签名（需要证书）
3. 提交样本到杀毒软件厂商

---

## 🤖 自动化构建 (GitHub Actions)

### 触发条件

自动构建会在以下情况触发：

1. **推送到主分支**
   ```bash
   git push origin main
   ```

2. **创建版本标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **手动触发**
   - 在 GitHub 仓库页面
   - Actions → Build OOPS Executable → Run workflow

### 下载构建产物

1. 进入 GitHub Actions 页面
2. 选择对应的构建任务
3. 下载 Artifacts 中的 `oops-windows-exe`

### 发布版本

创建版本标签会自动发布 Release：

```bash
# 1. 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 2. 推送标签
git push origin v1.0.0

# 3. GitHub Actions 会自动:
#    - 构建可执行文件
#    - 创建 Release
#    - 上传文件
```

---

## 📝 构建检查清单

构建前确认：

- [ ] 所有依赖已安装 (`pip install -r requirements.txt`)
- [ ] 代码无语法错误
- [ ] 测试通过 (`pytest tests/`)
- [ ] 版本号已更新 (`oops/__init__.py`)
- [ ] CHANGELOG 已更新
- [ ] 文档已更新

构建后确认：

- [ ] 可执行文件生成成功
- [ ] 文件大小合理（< 100MB）
- [ ] `--version` 显示正确
- [ ] `--help` 显示正常
- [ ] 基础功能测试通过
- [ ] 在干净环境中测试通过

---

## 🎯 优化建议

### 减小文件大小

1. **使用虚拟环境**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   ```

2. **只安装必要依赖**
   - 不要安装开发依赖（requirements-dev.txt）
   - 移除未使用的库

3. **启用压缩**
   - 使用 UPX 压缩
   - 在 build.spec 中设置 `upx=True`

### 提高构建速度

1. **使用缓存**
   - GitHub Actions 会自动缓存依赖
   - 本地构建可以保留 build 目录

2. **并行构建**
   - 多平台构建可以并行执行

---

## 📞 获取帮助

如果遇到构建问题：

1. 查看构建日志
2. 检查 [PyInstaller 文档](https://pyinstaller.org/)
3. 提交 Issue 到 GitHub

---

## 🔗 相关链接

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [UPX 压缩工具](https://upx.github.io/)

---

**最后更新**: 2024-11-22
**维护者**: OOPS开发团队
