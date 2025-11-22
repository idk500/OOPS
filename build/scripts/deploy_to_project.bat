@echo off
chcp 65001 >nul
echo ========================================
echo 部署 OOPS 到项目目录
echo ========================================
echo.

set "TARGET_DIR=ZenlessZoneZero-OneDragon-v2.3.3-Full-Environment"

if not exist "%TARGET_DIR%" (
    echo [ERROR] 目标目录不存在: %TARGET_DIR%
    pause
    exit /b 1
)

echo [1/4] 复制主程序...
copy /Y oops.py "%TARGET_DIR%\oops.py"

echo [2/4] 复制 oops 包...
xcopy /E /I /Y oops "%TARGET_DIR%\oops"

echo [3/4] 复制配置文件...
xcopy /E /I /Y configs "%TARGET_DIR%\configs"

echo [4/4] 创建 reports 目录...
if not exist "%TARGET_DIR%\reports" mkdir "%TARGET_DIR%\reports"

echo.
echo ========================================
echo ✅ 部署完成！
echo ========================================
echo.
echo 测试运行:
echo   cd %TARGET_DIR%
echo   python oops.py
echo.

pause
