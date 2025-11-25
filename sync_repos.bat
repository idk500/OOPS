@echo off
echo ========================================
echo OOPS Repository Sync
echo GitHub + Gitee 双备份
echo ========================================
echo.

echo [1/3] Pushing to GitHub...
git push origin main
if errorlevel 1 (
    echo ❌ GitHub push failed!
    pause
    exit /b 1
)
echo ✅ GitHub push successful
echo.

echo [2/3] Pushing to Gitee...
git push gitee main
if errorlevel 1 (
    echo ❌ Gitee push failed!
    pause
    exit /b 1
)
echo ✅ Gitee push successful
echo.

echo [3/3] Pushing tags...
git push origin --tags
git push gitee --tags
echo ✅ Tags pushed to both repositories
echo.

echo ========================================
echo ✅ Sync completed successfully!
echo ========================================
echo.
echo GitHub: https://github.com/idk500/OOPS
echo Gitee:  https://gitee.com/idk500/OOPS
echo.
pause
