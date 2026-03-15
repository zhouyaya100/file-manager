"""
系统配置文件
"""
import os
from datetime import timedelta

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(BASE_DIR, 'data', 'users')

# 安全密钥
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # 生产环境必须设置 SECRET_KEY 环境变量
    SECRET_KEY = os.urandom(32).hex()
    print('[WARN] SECRET_KEY not set, using random key (will change on restart)')
    print('       Production: export SECRET_KEY=your-secret-key')

# 数据库
DATABASE_PATH = os.path.join(BASE_DIR, 'file_manager.db')

# 会话配置
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# 文件上传配置
MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB 最大上传
ALLOWED_EXTENSIONS = None  # None 表示允许所有文件类型

# 权限级别
PERMISSION_READ = 'read'
PERMISSION_WRITE = 'write'
PERMISSION_ADMIN = 'admin'

# 日志配置
LOG_FILE = os.path.join(BASE_DIR, 'audit.log')
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 审计日志保留策略
AUDIT_LOG_MAX_RECORDS = 10000  # 最多保留 10000 条记录
AUDIT_LOG_MAX_AGE_DAYS = 90    # 最多保留 90 天的日志
