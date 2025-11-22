@echo off
chcp 65001 >nul
echo ========================================
echo OOPS 构建测试脚本
echo ========================================
echo.

if not exist dist\oops.exe (
    echo [ERROR] 未找到 dist\oops.exe
    echo 请先运行 build.bat 构建程序
    pause
    exit /b 1
)

echo [1/5] 测试版本信息...
dist\oops.exe --version
if %errorlevel% neq 0 (
    echo [ERROR] 版本信息测试失败
    pause
    exit /b 1
)
echo [PASS] 版本信息测试通过
echo.

echo [2/5] 测试帮助信息...
dist\oops.exe --help >nul
if %errorlevel% neq 0 (
    echo [ERROR] 帮助信息测试失败
    pause
    exit /b 1
)
echo [PASS] 帮助信息测试通过
echo.

echo [3/5] 测试列出项目...
dist\oops.exe --list-projects
if %errorlevel% neq 0 (
    echo [ERROR] 列出项目测试失败
    pause
    exit /b 1
)
echo [PASS] 列出项目测试通过
echo.

echo [4/5] 测试创建配置...
dist\oops.exe --create-config
if %errorlevel% neq 0 (
    echo [ERROR] 创建配置测试失败
    pause
    exit /b 1
)
echo [PASS] 创建配置测试通过
echo.

echo [5/5] 检查文件大小...
for %%A in (dist\oops.exe) do (
    set size=%%~zA
    set /a sizeMB=%%~zA/1024/1024
)
echo 文件大小: %sizeMB% MB
if %sizeMB% GTR 100 (
    echo [WARN] 文件过大 ^(^> 100MB^)，建议优化
) else (
    echo [PASS] 文件大小合理
)
echo.

echo ========================================
echo ✅ 所有测试通过！
echo ========================================
echo.
echo 可执行文件: dist\oops.exe
echo 文件大小: %sizeMB% MB
echo.
echo 💡 下一步:
echo   1. 复制 oops.exe 到项目根目录
echo   2. 双击运行测试
echo.

pause
