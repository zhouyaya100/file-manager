#!/usr/bin/env python3
"""
File Manager 启动脚本
支持开发模式和生产模式
"""

import os
import sys
import logging
import argparse

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """检查运行环境"""
    print("=" * 60)
    print("  FileHub 多用户文件管理系统")
    print("=" * 60)
    print()
    
    # Python 版本检查
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        logger.error("Python 3.8+ required, current: %s", '.'.join(map(str, python_version[:3])))
        sys.exit(1)
    
    print(f"[OK] Python 版本：{python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要目录
    required_dirs = ['data', 'data/users', 'static', 'templates']
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"[OK] 创建目录：{dir_name}")
        else:
            print(f"[OK] 目录存在：{dir_name}")
    
    # 检查数据库
    db_path = os.path.join(base_dir, 'file_manager.db')
    if os.path.exists(db_path):
        print(f"[OK] 数据库文件：file_manager.db")
    else:
        print(f"[WARN] 数据库文件不存在，首次启动将自动创建")
    
    print()


def start_development(host='127.0.0.1', port=5000, debug=True):
    """开发模式启动"""
    from app import app
    
    logger.info("启动模式：开发模式 (Development)")
    logger.info(f"访问地址：http://{host}:{port}")
    logger.info("默认管理员：admin / Admin@123")
    print()
    
    app.run(host=host, port=port, debug=debug, use_reloader=debug)


def start_production():
    """生产模式启动（使用 Gunicorn）"""
    import subprocess
    
    logger.info("启动模式：生产模式 (Production with Gunicorn)")
    
    # 检查 Gunicorn 是否安装
    try:
        import gunicorn
    except ImportError:
        logger.error("Gunicorn 未安装！运行：pip install gunicorn")
        sys.exit(1)
    
    # 启动 Gunicorn
    gunicorn_cmd = [
        sys.executable, '-m', 'gunicorn',
        '-c', 'gunicorn.conf.py',
        'app:app'
    ]
    
    logger.info(f"执行命令：{' '.join(gunicorn_cmd)}")
    subprocess.run(gunicorn_cmd)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FileHub 文件管理系统')
    parser.add_argument('--host', default='127.0.0.1', help='绑定地址 (默认：127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='端口号 (默认：5000)')
    parser.add_argument('--production', action='store_true', help='生产模式启动')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    # 环境检查
    check_environment()
    
    # 启动服务
    if args.production:
        start_production()
    else:
        start_development(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
