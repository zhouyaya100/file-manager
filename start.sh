#!/bin/bash

echo "========================================"
echo "  多用户文件管理系统"
echo "========================================"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[提示] 未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "[提示] 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "[正在] 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "[检查] 依赖包..."
pip show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[安装] 依赖包中..."
    pip install -r requirements.txt
fi

# 启动应用
echo ""
echo "[启动] 应用服务器..."
echo "访问地址：http://localhost:5000"
echo "默认管理员：admin / Admin@123"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python3 app.py
