# Build 相关文件

本目录包含所有构建相关的文件和文档。

## 📁 目录结构

```
build/
├── README.md                    # 本文件
├── scripts/                     # 构建脚本
│   ├── build.bat               # Windows构建脚本
│   ├── build.sh                # Linux/macOS构建脚本
│   ├── test_build.bat          # 构建测试脚本
│   └── deploy_to_project.bat   # 项目部署脚本
├── config/                      # 构建配置
│   ├── build.spec              # PyInstaller配置
│   └── .gitignore              # 构建产物忽略
├── docs/                        # 构建文档
│   ├── BUILD.md                # 详细构建指南
│   ├── BUILD_SUMMARY.md        # 构建系统总结
│   ├── BUILD_QUICK_REFERENCE.md # 快速参考
│   └── RELEASE_CHECKLIST.md    # 发布检查清单
└── workflows/                   # CI/CD配置
    └── build.yml               # GitHub Actions工作流
```

## 🚀 快速开始

```bash
# Windows
build\scripts\build.bat

# Linux/macOS
chmod +x build/scripts/build.sh
build/scripts/build.sh
```

## 📚 文档

- [详细构建指南](docs/BUILD.md)
- [快速参考](docs/BUILD_QUICK_REFERENCE.md)
- [发布检查清单](docs/RELEASE_CHECKLIST.md)
