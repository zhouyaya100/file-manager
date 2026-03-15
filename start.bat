@echo off
chcp 65001 >nul
echo ========================================
echo   多用户文件管理系统
echo ========================================
echo.

cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv" (
    echo [提示] 未检测到虚拟环境，正在创建...
    python -m venv venv
    echo [提示] 虚拟环境创建完成
)

REM 激活虚拟环境
echo [正在] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo [检查] 依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 依赖包中...
    pip install -r requirements.txt
)

REM 启动应用
echo.
echo [启动] 应用服务器...
echo 访问地址：http://localhost:5000
echo 默认管理员：admin / Admin@123
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python app.py

pause
