# OOPS 配置指南

## 快速开始

### 1. 配置项目路径

首次使用 OOPS 时，需要配置项目的安装路径。

打开配置文件：`configs/zenless_zone_zero.yaml`

找到 `install_path` 配置项，填写你的项目安装路径：

```yaml
project:
  paths:
    install_path: 'E:/ZZZ-1D'  # ← 修改为你的实际路径
```

### 2. 支持的路径格式

#### 绝对路径（推荐）
```yaml
install_path: 'E:/ZZZ-1D'
install_path: 'C:/Games/ZenlessZoneZero-OneDragon'
```

#### 环境变量
```yaml
install_path: '${ZZZ_INSTALL_PATH}'
install_path: '${USERPROFILE}/Desktop/ZZZ-1D'
```

设置环境变量（Windows）：
```cmd
setx ZZZ_INSTALL_PATH "E:\ZZZ-1D"
```

#### 相对路径
```yaml
install_path: '../ZenlessZoneZero-OneDragon'
install_path: './ZZZ-1D'
```

#### 自动检测
```yaml
install_path: 'auto'
```

自动检测会在以下位置查找项目：
- 当前目录
- 父目录（向上3层）
- 同级目录（常见项目名称）

### 3. 运行检测

配置完成后，运行检测：

```bash
# 检测指定项目
python oops.py --project zenless_zone_zero

# 或使用 exe 文件
oops.exe --project zenless_zone_zero
```

## 常见问题

### Q: 如何找到我的项目安装路径？

A: 找到 `OneDragon-Launcher.exe` 所在的文件夹，那就是你的项目安装路径。

例如：
- 如果启动器在 `E:\ZZZ-1D\OneDragon-Launcher.exe`
- 那么安装路径就是 `E:/ZZZ-1D`

### Q: 路径中的斜杠应该用 `/` 还是 `\`？

A: 两种都可以，但推荐使用 `/`（正斜杠）：
- ✅ 推荐：`E:/ZZZ-1D`
- ✅ 也可以：`E:\ZZZ-1D`
- ✅ 也可以：`E:\\ZZZ-1D`（双反斜杠）

### Q: 配置后仍然提示路径错误？

A: 请检查：
1. 路径是否正确（没有拼写错误）
2. 路径是否存在
3. 路径中是否包含 `OneDragon-Launcher.exe`
4. YAML 格式是否正确（注意缩进）

### Q: 可以使用中文路径吗？

A: 可以，但不推荐。建议使用英文路径以避免潜在问题。

### Q: 如何为多个项目配置不同的路径？

A: 每个项目都有独立的配置文件：
- `configs/zenless_zone_zero.yaml` - 绝区零项目
- `configs/generic_python.yaml` - 通用 Python 项目
- 等等...

分别编辑对应的配置文件即可。

## 高级配置

### 使用环境变量

1. 设置环境变量：
```cmd
# Windows CMD
setx ZZZ_INSTALL_PATH "E:\ZZZ-1D"

# Windows PowerShell
[Environment]::SetEnvironmentVariable("ZZZ_INSTALL_PATH", "E:\ZZZ-1D", "User")

# Linux/Mac
export ZZZ_INSTALL_PATH="/home/user/ZZZ-1D"
```

2. 在配置文件中使用：
```yaml
install_path: '${ZZZ_INSTALL_PATH}'
```

### 自动检测配置

如果你的项目在以下位置，可以使用自动检测：
- OOPS 的父目录
- OOPS 的同级目录
- 常见的项目名称（ZenlessZoneZero-OneDragon, ZZZ-1D 等）

```yaml
install_path: 'auto'
```

## 需要帮助？

如果遇到问题，请：
1. 查看日志文件：`oops.log`
2. 查看生成的报告：`reports/` 目录
3. 提交 Issue 到 GitHub

---

**提示**：配置完成后，建议运行一次检测确认配置正确。
