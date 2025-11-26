@echo off
chcp 65001 >nul
echo ========================================
echo 游戏抢单系统 - Windows 正式版打包
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/5] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/5] 开始打包正式版...
pyinstaller 游戏抢单系统正式版.spec
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/5] 清理临时文件...
if exist build rmdir /s /q build

echo.
echo [5/5] 打包完成！
echo.
echo ========================================
echo 可执行文件位置: dist\游戏抢单系统正式版.exe
echo ========================================
echo.
echo 重要提示：
echo - 首次运行可能会被杀毒软件拦截，请添加信任
echo - 程序需要网络连接才能正常工作
echo - 配置文件会自动生成在用户目录的 .game_order_grabber 文件夹
echo - 本版本为正式版，已优化文件大小和启动速度
echo.
pause
