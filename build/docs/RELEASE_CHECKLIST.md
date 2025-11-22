# 发布检查清单

## 📋 发布前检查

### 代码质量
- [ ] 所有测试通过 (`pytest tests/`)
- [ ] 代码格式化完成 (`black oops/`)
- [ ] 无语法错误 (`python -m py_compile oops.py`)
- [ ] 无类型错误 (`mypy oops/` - 可选)

### 版本信息
- [ ] 更新版本号 (`oops/__init__.py`)
- [ ] 更新 CHANGELOG.md
- [ ] 更新 README.md（如有新功能）
- [ ] 更新文档（如有变更）

### 功能测试
- [ ] 基础功能测试
  - [ ] `python oops.py --version`
  - [ ] `python oops.py --help`
  - [ ] `python oops.py --list-projects`
  - [ ] `python oops.py` (运行检测)
- [ ] 项目自动检测测试
- [ ] 报告生成测试
- [ ] 浏览器自动打开测试

### 文档检查
- [ ] README.md 最新
- [ ] USER_GUIDE.md 最新
- [ ] QUICKSTART.md 最新
- [ ] BUILD.md 最新
- [ ] CHANGELOG.md 已更新

---

## 🔨 构建检查

### 本地构建
- [ ] 运行 `build.bat` (Windows)
- [ ] 运行 `build.sh` (Linux/macOS)
- [ ] 构建成功无错误
- [ ] 生成 `dist/oops.exe`

### 构建测试
- [ ] 运行 `test_build.bat`
- [ ] 所有测试通过
- [ ] 文件大小合理 (< 100MB)

### 功能测试（使用构建的exe）
- [ ] `dist\oops.exe --version`
- [ ] `dist\oops.exe --help`
- [ ] `dist\oops.exe --list-projects`
- [ ] `dist\oops.exe` (完整运行)
- [ ] 报告生成正常
- [ ] 浏览器自动打开

### 兼容性测试
- [ ] Windows 10 测试
- [ ] Windows 11 测试
- [ ] 干净环境测试（无Python）
- [ ] 不同路径测试
- [ ] 中文路径测试

---

## 🚀 发布流程

### 1. 准备发布

```bash
# 1. 确保在主分支
git checkout main
git pull origin main

# 2. 更新版本号
# 编辑 oops/__init__.py
__version__ = "1.0.0"

# 3. 更新 CHANGELOG.md
# 添加新版本的更新内容

# 4. 提交更改
git add .
git commit -m "chore: prepare release v1.0.0"
git push origin main
```

### 2. 创建标签

```bash
# 创建带注释的标签
git tag -a v1.0.0 -m "Release version 1.0.0

## 新功能
- 项目自动检测
- 改进的报告输出
- 知识库集成

## Bug修复
- 修复路径验证问题
- 修复DirectX检测弹窗

## 文档
- 新增用户指南
- 完善构建文档
"

# 推送标签
git push origin v1.0.0
```

### 3. GitHub Actions 自动构建

- [ ] 检查 GitHub Actions 运行状态
- [ ] 等待构建完成
- [ ] 下载并测试构建产物

### 4. 创建 Release

GitHub Actions 会自动创建 Release，检查：

- [ ] Release 已创建
- [ ] 文件已上传
  - [ ] oops.exe
  - [ ] README.md
  - [ ] USER_GUIDE.md
- [ ] Release 说明完整
- [ ] 标签正确

### 5. 手动补充（如需要）

如果需要手动创建或编辑 Release：

1. 进入 GitHub 仓库
2. Releases → Draft a new release
3. 选择标签: v1.0.0
4. 填写 Release 标题和说明
5. 上传文件
6. Publish release

---

## 📢 发布后

### 通知用户
- [ ] 更新项目主页
- [ ] 发布公告
- [ ] 更新文档链接
- [ ] 社交媒体通知（如适用）

### 监控反馈
- [ ] 关注 GitHub Issues
- [ ] 收集用户反馈
- [ ] 记录问题和改进建议

### 文档更新
- [ ] 更新在线文档
- [ ] 更新下载链接
- [ ] 更新版本说明

---

## 🐛 回滚流程

如果发现严重问题需要回滚：

### 1. 标记为 Pre-release

1. 进入 GitHub Release 页面
2. 编辑对应的 Release
3. 勾选 "This is a pre-release"
4. 添加警告说明

### 2. 发布修复版本

```bash
# 修复问题后
git tag -a v1.0.1 -m "Hotfix: 修复xxx问题"
git push origin v1.0.1
```

### 3. 删除问题版本（慎用）

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 在 GitHub 上删除 Release
```

---

## 📊 发布统计

记录每次发布的关键指标：

### v1.0.0 (示例)
- **发布日期**: 2024-11-22
- **文件大小**: 45 MB
- **下载次数**: -
- **问题报告**: -
- **用户反馈**: -

---

## 💡 最佳实践

### 版本号规范

遵循语义化版本 (Semantic Versioning):

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

示例:
- `1.0.0` - 首个稳定版本
- `1.1.0` - 新增功能
- `1.1.1` - Bug修复
- `2.0.0` - 重大更新

### 发布频率

- **主版本**: 每季度或半年
- **次版本**: 每月或每两周
- **修订版**: 按需发布（Bug修复）

### 测试覆盖

- **单元测试**: 80%+ 覆盖率
- **集成测试**: 核心功能全覆盖
- **手动测试**: 每次发布前完整测试

---

**模板版本**: 1.0
**最后更新**: 2024-11-22
