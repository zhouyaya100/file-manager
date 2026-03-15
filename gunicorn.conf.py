# Gunicorn 配置文件
# 生产环境使用

# 绑定地址和端口
bind = "127.0.0.1:5000"

# 工作进程数（建议：CPU 核心数 * 2 + 1）
workers = 4

# 每个工作进程的线程数
threads = 2

# 工作进程类型
worker_class = "sync"

# 超时设置（秒）
timeout = 120

# 保持连接超时
keepalive = 5

# 日志文件路径
accesslog = "/var/log/file_manager/access.log"
errorlog = "/var/log/file_manager/error.log"

# 日志级别
loglevel = "info"

# 进程命名
proc_name = "file_manager"

# 工作目录
chdir = "/path/to/file_manager"

# 用户和组（生产环境建议）
# user = "www-data"
# group = "www-data"

# 守护进程模式
daemon = False

# PID 文件
pidfile = "/var/run/file_manager.pid"

# 每个工作进程的最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50
