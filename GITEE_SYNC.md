# Gitee 镜像同步说明

## 📦 仓库地址

- **GitHub（主仓库）**: https://github.com/idk500/OOPS
- **Gitee（镜像）**: https://gitee.com/idk500/OOPS

## 🔄 同步方式

### 自动同步（推荐）

使用 `sync_repos.bat` 脚本一键同步到 GitHub 和 Gitee：

```bash
# 双击运行
sync_repos.bat
```

### 手动同步

```bash
# 推送到 GitHub
git push origin main
git push origin --tags

# 推送到 Gitee
git push gitee main
git push gitee --tags
```

## 📝 配置远程仓库

如果你 clone 的是 GitHub 仓库，需要添加 Gitee 远程：

```bash
git remote add gitee https://gitee.com/idk500/OOPS.git
```

如果你 clone 的是 Gitee 仓库，需要添加 GitHub 远程：

```bash
git remote add github https://github.com/idk500/OOPS.git
```

查看所有远程仓库：

```bash
git remote -v
```

## 🎯 发布流程

1. **提交代码**
   ```bash
   git add .
   git commit -m "your message"
   ```

2. **同步到两个仓库**
   ```bash
   sync_repos.bat
   # 或手动推送
   git push origin main
   git push gitee main
   ```

3. **创建版本标签**
   ```bash
   git tag -a v0.x.x -m "Release v0.x.x"
   git push origin v0.x.x
   git push gitee v0.x.x
   ```

4. **GitHub Actions 自动构建**
   - GitHub 会自动触发 CI/CD
   - 自动构建 Windows exe
   - 自动创建 Release

5. **手动同步 Gitee Release**
   - 从 GitHub Release 下载构建好的文件
   - 在 Gitee 创建对应的 Release
   - 上传相同的文件

## 🚀 GitHub Actions

GitHub Actions 会在以下情况自动运行：

- **CI**: 每次 push 到 main 分支
- **Release**: 推送版本标签（如 v0.2.1）

Gitee 目前不支持 Actions，需要手动创建 Release。

## 📊 同步状态

| 内容 | GitHub | Gitee | 说明 |
|------|--------|-------|------|
| 代码 | ✅ 自动 | ✅ 手动 | 使用 sync_repos.bat |
| 标签 | ✅ 自动 | ✅ 手动 | 使用 sync_repos.bat |
| Release | ✅ 自动 | ⚠️ 手动 | GitHub Actions 自动构建 |
| Issues | ✅ | ❌ | 仅 GitHub |
| Actions | ✅ | ❌ | 仅 GitHub |

## 💡 建议

- **开发**: 使用 GitHub（支持 Actions）
- **发布**: 同时发布到 GitHub 和 Gitee
- **国内用户**: 推荐从 Gitee 下载（速度更快）
- **国际用户**: 推荐从 GitHub 下载

## 🔗 相关链接

- [GitHub Repository](https://github.com/idk500/OOPS)
- [Gitee Repository](https://gitee.com/idk500/OOPS)
- [GitHub Releases](https://github.com/idk500/OOPS/releases)
- [Gitee Releases](https://gitee.com/idk500/OOPS/releases)
