# 构建快速参考

## 🚀 一键构建

### Windows
```bash
build.bat
```

### Linux/macOS
```bash
chmod +x build.sh
./build.sh
```

---

## 📦 输出文件

```
dist/oops.exe    # Windows
dist/oops        # Linux/macOS
```

---

## 🧪 测试构建

```bash
# Windows
test_build.bat

# 手动测试
dist\oops.exe --version
dist\oops.exe --help
dist\oops.exe
```

---

## 🏷️ 发布版本

```bash
# 1. 更新版本号
# 编辑 oops/__init__.py

# 2. 提交更改
git add .
git commit -m "chore: prepare release v1.0.0"
git push

# 3. 创建标签
git tag v1.0.0
git push origin v1.0.0

# 4. GitHub Actions 自动构建和发布
```

---

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `build.bat` | 本地构建 |
| `test_build.bat` | 测试构建 |
| `pyinstaller --clean build.spec` | 手动构建 |
| `git tag v1.0.0` | 创建标签 |
| `git push origin v1.0.0` | 推送标签 |

---

## 📁 关键文件

| 文件 | 用途 |
|------|------|
| `build.spec` | PyInstaller 配置 |
| `build.bat` | Windows 构建脚本 |
| `.github/workflows/build.yml` | CI/CD 配置 |
| `BUILD.md` | 详细文档 |

---

## ⚡ 快速故障排除

| 问题 | 解决方案 |
|------|----------|
| 缺少模块 | 添加到 `build.spec` 的 `hiddenimports` |
| 找不到文件 | 添加到 `build.spec` 的 `datas` |
| 文件过大 | 添加到 `build.spec` 的 `excludes` |
| 杀毒误报 | 添加到白名单 |

---

**快速链接**:
- [完整文档](BUILD.md)
- [发布清单](RELEASE_CHECKLIST.md)
- [构建总结](BUILD_SUMMARY.md)
