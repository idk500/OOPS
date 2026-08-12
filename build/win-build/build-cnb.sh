#!/bin/bash
# build/win-build/build-cnb.sh —— CNB 流水线中构建 Windows exe 并打包
# 由 .cnb.yml 的 tag_push 事件调用,在 build/win-build/Dockerfile 提供的
# Wine + Windows Python 环境中运行。
#
# 流程:
#   1. 解析当前 tag
#   2. 用 Wine + Windows Python 运行 PyInstaller 构建 oops.exe
#   3. 组装 release 包(exe + configs + 文档)
#   4. 打 zip:oops-windows-x64_<tag>.zip

set -euo pipefail

# 工作目录 = CNB 流水线当前工作区(仓库根)
WORKSPACE="$(pwd)"
echo "[INFO] 工作目录: $WORKSPACE"

# ---- 解析 tag ----
TAG="$(git describe --tags --exact-match HEAD 2>/dev/null || echo '')"
if [ -z "$TAG" ]; then
  echo "[ERROR] 无法解析当前 tag(git describe --tags --exact-match 失败)"
  exit 1
fi
echo "[INFO] 构建 tag=$TAG 的 Windows exe"

# ---- Wine / Python 路径 ----
WINPY="C:\\Python311\\python.exe"
export WINEDEBUG=-all
export WINEPREFIX=/root/.wine
export WINEARCH=win64
export DISPLAY=:99
WINE_CMD="${WINE_CMD:-wine64}"
if ! command -v "$WINE_CMD" >/dev/null 2>&1; then
  echo "[WARN] wine64 不可用,尝试 wine"
  WINE_CMD="wine"
fi

# ---- 清理旧构建产物 ----
rm -rf "${WORKSPACE}/build" "${WORKSPACE}/dist" "${WORKSPACE}"/*.spec "${WORKSPACE}/release-package"
mkdir -p "${WORKSPACE}/release-package"

# ---- 用 PyInstaller 构建 Windows exe ----
echo "[1/5] PyInstaller 构建 oops.exe ..."
cd "${WORKSPACE}"
xvfb-run -a "${WINE_CMD}" "${WINPY}" -m PyInstaller \
    --onefile \
    --name oops \
    --icon "${WORKSPACE}/oops.ico" \
    --collect-all tkinter \
    --distpath "${WORKSPACE}/dist" \
    --workpath "${WORKSPACE}/build" \
    --specpath "${WORKSPACE}" \
    "${WORKSPACE}/oops.py"

if [ ! -f "${WORKSPACE}/dist/oops.exe" ]; then
  echo "[ERROR] PyInstaller 构建失败,未生成 oops.exe"
  ls -la "${WORKSPACE}/dist/" 2>/dev/null || true
  exit 1
fi
echo "[OK] 生成 dist/oops.exe ($(du -h "${WORKSPACE}/dist/oops.exe" | cut -f1))"

# ---- 组装 release 包 ----
echo "[2/5] 组装 release 包 ..."
mv "${WORKSPACE}/dist/oops.exe" "${WORKSPACE}/release-package/oops-windows-x64.exe"
cp -r "${WORKSPACE}/configs" "${WORKSPACE}/release-package/"
cp "${WORKSPACE}/README.md" "${WORKSPACE}/release-package/" 2>/dev/null || true
cp "${WORKSPACE}/QUICKSTART.md" "${WORKSPACE}/release-package/" 2>/dev/null || true
cp "${WORKSPACE}/CHANGELOG.md" "${WORKSPACE}/release-package/" 2>/dev/null || true

# ---- 打 zip ----
echo "[3/5] 打包 zip ..."
ZIP_NAME="oops-windows-x64_${TAG}.zip"
cd "${WORKSPACE}/release-package"
zip -r "${WORKSPACE}/${ZIP_NAME}" ./*
cd "${WORKSPACE}"
ls -la "${ZIP_NAME}"
echo "[OK] 生成 ${ZIP_NAME} ($(du -h "${ZIP_NAME}" | cut -f1))"

# ---- 输出 tag 供后续 stage 使用 ----
echo "ASSET=${ZIP_NAME}" > "${WORKSPACE}/workspace.env"
echo "TAG=${TAG}" >> "${WORKSPACE}/workspace.env"
echo "[4/5] 构建完成: ${TAG} -> ${ZIP_NAME}"
