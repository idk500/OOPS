@echo off
chcp 65001 >nul
echo ========================================
echo OOPS 构建脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 安装PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/5] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist oops.spec del /q oops.spec

echo.
echo [3/5] 开始构建...
pyinstaller --clean --noconfirm build\config\build.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 构建失败！
    pause
    exit /b 1
)

echo.
echo [4/5] 测试可执行文件...
dist\oops.exe --version
if %errorlevel% neq 0 (
    echo [ERROR] 可执行文件测试失败！
    pause
    exit /b 1
)

echo.
echo [5/5] 构建完成！
echo.
echo ========================================
echo 输出文件: dist\oops.exe
echo 文件大小: 
for %%A in (dist\oops.exe) do echo   %%~zA 字节
echo ========================================
echo.
echo 💡 提示:
echo   1. 将 oops.exe 复制到项目根目录
echo   2. 双击运行即可
echo.

pause
