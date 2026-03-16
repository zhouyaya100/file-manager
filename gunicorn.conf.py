# Gunicorn 配置文件
# 生产环境使用

import os
import multiprocessing

# ==================== 基础配置 ====================

# 绑定地址和端口
# 0.0.0.0 允许外部访问，127.0.0.1 仅本地访问
bind = os.environ.get('GUNICORN_BIND', "0.0.0.0:5000")

# 工作进程数（建议：CPU 核心数 * 2 + 1）
cpu_count = multiprocessing.cpu_count()
workers = int(os.environ.get('GUNICORN_WORKERS', cpu_count * 2 + 1))

# 每个工作进程的线程数
threads = int(os.environ.get('GUNICORN_THREADS', 2))

# 工作进程类型
# sync: 同步 (默认)
# gevent: 异步 (高并发场景)
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')

# ==================== 超时设置 ====================

# 工作进程超时（秒）- 超过此时间的工作进程将被杀死并重启
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))

# 优雅超时（秒）- 工作进程重启前等待当前请求完成的时间
graceful_timeout = 30

# 保持连接超时（秒）
keepalive = 5

# ==================== 日志配置 ====================

# 日志文件路径
log_dir = os.environ.get('LOG_DIR', '/var/log/file_manager')
os.makedirs(log_dir, exist_ok=True)

accesslog = os.path.join(log_dir, 'access.log')
errorlog = os.path.join(log_dir, 'error.log')

# 日志级别：debug, info, warning, error, critical
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ==================== 进程管理 ====================

# 进程命名
proc_name = "file_manager"

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 守护进程模式
daemon = False

# PID 文件
pidfile = os.environ.get('PIDFILE', '/var/run/file_manager.pid')

# PID 文件创建
def on_starting(server):
    """服务启动前"""
    pid_dir = os.path.dirname(pidfile)
    if pid_dir and not os.path.exists(pid_dir):
        os.makedirs(pid_dir, exist_ok=True)

# ==================== 性能优化 ====================

# 每个工作进程的最大请求数（防止内存泄漏）
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 50))

# 工作进程队列大小
backlog = int(os.environ.get('GUNICORN_BACKLOG', 2048))

# ==================== 安全配置 ====================

# 限制请求头大小
limit_request_line = int(os.environ.get('GUNICORN_LIMIT_REQUEST_LINE', 4094))
limit_request_fields = int(os.environ.get('GUNICORN_LIMIT_REQUEST_FIELDS', 100))
limit_request_field_size = int(os.environ.get('GUNICORN_LIMIT_REQUEST_FIELD_SIZE', 8190))

# ==================== 用户和组（生产环境建议） ====================

# 在 Linux 上以低权限用户运行
# user = "www-data"
# group = "www-data"

# ==================== SSL/TLS（生产环境推荐） ====================

# keyfile = "/path/to/ssl/server.key"
# certfile = "/path/to/ssl/server.crt"

# ==================== 监控和健康检查 ====================

def post_fork(server, worker):
    """工作进程启动后"""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    """工作进程被中止时"""
    worker.log.info("Worker received SIGABRT")

def worker_exit(server, worker):
    """工作进程退出时"""
    worker.log.info(f"Worker exiting (pid: {worker.pid})")

def on_exit(server):
    """服务退出时"""
    server.log.info("Gunicorn server is shutting down")

# ==================== 环境变量快速参考 ====================

# 可通过环境变量覆盖的配置:
# - GUNICORN_BIND: 绑定地址 (默认：0.0.0.0:5000)
# - GUNICORN_WORKERS: 工作进程数 (默认：CPU*2+1)
# - GUNICORN_THREADS: 每进程线程数 (默认：2)
# - GUNICORN_WORKER_CLASS: 工作类型 (默认：sync)
# - GUNICORN_TIMEOUT: 超时时间 (默认：120)
# - GUNICORN_LOGLEVEL: 日志级别 (默认：info)
# - LOG_DIR: 日志目录 (默认：/var/log/file_manager)
# - PIDFILE: PID 文件路径 (默认：/var/run/file_manager.pid)
# - GUNICORN_MAX_REQUESTS: 最大请求数 (默认：1000)
