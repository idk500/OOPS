#!/bin/bash

echo "========================================"
echo "OOPS 构建脚本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

echo "[1/5] 检查依赖..."
if ! python3 -m pip show pyinstaller &> /dev/null; then
    echo "[INFO] 安装PyInstaller..."
    python3 -m pip install pyinstaller
fi

echo ""
echo "[2/5] 清理旧文件..."
rm -rf build dist oops.spec

echo ""
echo "[3/5] 开始构建..."
pyinstaller --clean --noconfirm build/config/build.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] 构建失败！"
    exit 1
fi

echo ""
echo "[4/5] 测试可执行文件..."
./dist/oops --version

if [ $? -ne 0 ]; then
    echo "[ERROR] 可执行文件测试失败！"
    exit 1
fi

echo ""
echo "[5/5] 构建完成！"
echo ""
echo "========================================"
echo "输出文件: dist/oops"
echo "文件大小: $(du -h dist/oops | cut -f1)"
echo "========================================"
echo ""
echo "💡 提示:"
echo "  1. 将 oops 复制到项目根目录"
echo "  2. 运行: ./oops"
echo ""
