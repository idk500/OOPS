# OOPS 发布指南

## 🚀 快速发布流程

### 1. 准备发布

```bash
# 1. 确保在main分支
git checkout main
git pull origin main

# 2. 更新版本号
# 编辑 oops/__init__.py
__version__ = "1.1.0"

# 3. 更新CHANGELOG.md
# 添加新版本的更新内容

# 4. 提交更改
git add oops/__init__.py CHANGELOG.md
git commit -m "chore: 准备发布 v1.1.0"
git push origin main
```

### 2. 创建版本标签

```bash
# 创建标签
git tag -a v1.1.0 -m "OOPS v1.1.0 - 版本说明"

# 推送标签（触发自动构建）
git push origin v1.1.0
```

### 3. 等待自动构建

1. 访问 GitHub Actions 页面
2. 查看 "Build and Release" 工作流
3. 等待构建完成（约10-15分钟）

### 4. 验证发布

1. 访问 GitHub Releases 页面
2. 确认新版本已创建
3. 下载并测试各平台的可执行文件

---

## 📋 详细发布检查清单

### 发布前检查

- [ ] 所有功能已完成并测试
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] 没有未提交的更改

### 版本号规范

遵循语义化版本 (Semantic Versioning):

- **主版本号** (Major): 不兼容的API更改
- **次版本号** (Minor): 向后兼容的功能新增
- **修订号** (Patch): 向后兼容的问题修正

示例:
- `v1.0.0` → `v1.0.1` - Bug修复
- `v1.0.0` → `v1.1.0` - 新功能
- `v1.0.0` → `v2.0.0` - 重大更改

### CHANGELOG 格式

```markdown
## v1.1.0 (2025-11-23)

### ✨ 新功能
- 添加XXX功能
- 支持XXX

### 🐛 Bug修复
- 修复XXX问题
- 解决XXX错误

### 📝 文档
- 更新XXX文档
- 添加XXX说明

### 🔧 其他
- 优化XXX性能
- 重构XXX模块
```

---

## 🔄 发布类型

### 正式版本 (Stable Release)

```bash
# 格式: vX.Y.Z
git tag -a v1.0.0 -m "OOPS v1.0.0 - 首个正式版本"
git push origin v1.0.0
```

### 预发布版本 (Pre-release)

```bash
# Beta版本
git tag -a v1.1.0-beta.1 -m "OOPS v1.1.0-beta.1"
git push origin v1.1.0-beta.1

# RC版本
git tag -a v1.1.0-rc.1 -m "OOPS v1.1.0-rc.1"
git push origin v1.1.0-rc.1
```

### 热修复版本 (Hotfix)

```bash
# 从main分支创建hotfix分支
git checkout -b hotfix/v1.0.1 main

# 修复问题
# ... 编写代码 ...

# 提交并合并
git add .
git commit -m "fix: 修复XXX问题"
git checkout main
git merge hotfix/v1.0.1

# 创建标签
git tag -a v1.0.1 -m "OOPS v1.0.1 - 修复XXX问题"
git push origin v1.0.1
```

---

## 🛠️ 手动构建（备用方案）

如果自动构建失败，可以手动构建：

### Windows

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 构建
cd build/scripts
./build.bat

# 产物位置
# dist/oops.exe
```

### Linux

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 构建
cd build/scripts
./build.sh

# 产物位置
# dist/oops
```

### macOS

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 构建
cd build/scripts
./build.sh

# 产物位置
# dist/oops
```

---

## 📝 发布说明模板

```markdown
## OOPS vX.Y.Z

**发布日期**: YYYY-MM-DD

### 🎉 亮点

简要介绍本版本的主要特性。

### ✨ 新功能

- 功能1
- 功能2

### 🐛 Bug修复

- 修复1
- 修复2

### 📝 文档

- 文档更新1
- 文档更新2

### 🔧 其他改进

- 改进1
- 改进2

### 📦 下载

- Windows: [oops-windows-x64.exe](链接)
- Linux: [oops-linux-x64](链接)
- macOS: [oops-macos-x64](链接)

### 📚 文档

- [快速开始](链接)
- [用户指南](链接)
- [更新日志](链接)
```

---

## 🐛 故障排除

### 问题: 标签推送失败

```bash
# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0

# 重新创建
git tag -a v1.0.0 -m "新的说明"
git push origin v1.0.0
```

### 问题: 构建失败

1. 查看 GitHub Actions 日志
2. 本地复现问题
3. 修复后重新推送标签

### 问题: Release 创建失败

1. 检查 GitHub Token 权限
2. 确认 Actions 已启用
3. 查看工作流日志

---

## 📊 发布后任务

### 1. 验证发布

- [ ] 下载各平台可执行文件
- [ ] 测试基本功能
- [ ] 检查版本号显示

### 2. 更新文档

- [ ] 更新 README.md（如需要）
- [ ] 更新在线文档
- [ ] 更新示例

### 3. 通知用户

- [ ] 发布公告
- [ ] 更新社交媒体
- [ ] 通知相关社区

### 4. 监控反馈

- [ ] 关注 GitHub Issues
- [ ] 收集用户反馈
- [ ] 记录问题和改进建议

---

## 🔐 安全注意事项

### 敏感信息

- 不要在代码中硬编码密钥
- 使用 GitHub Secrets 存储敏感配置
- 审查依赖的安全漏洞

### 发布权限

- 只有维护者可以推送标签
- 保护 main 分支
- 要求 PR 审查

---

## 📚 相关文档

- **[GitHub Actions文档](GITHUB_ACTIONS.md)** - 自动化工作流
- **[构建文档](../../build/docs/BUILD.md)** - 本地构建
- **[发布检查清单](RELEASE_CHECKLIST_v1.0.0.md)** - 详细检查清单

---

**发布流程自动化，让发布更简单！** 🚀
