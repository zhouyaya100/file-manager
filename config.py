"""
系统配置文件
"""
import os
from datetime import timedelta

# ==================== 基础路径 ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(BASE_DIR, 'data', 'users')

# ==================== 安全密钥 ====================

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # 开发环境使用固定密钥 (生产环境必须设置 SECRET_KEY 环境变量)
    SECRET_KEY = 'dev-secret-key-change-in-production-2026'
    # 生产环境生成方式：python -c "import secrets; print(secrets.token_hex(32))"

# ==================== 数据库配置 ====================

DATABASE_PATH = os.path.join(BASE_DIR, 'file_manager.db')

# 生产环境可切换到 PostgreSQL/MySQL:
# DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')

# ==================== 会话配置 ====================

PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SECURE = False  # 生产环境设为 True (HTTPS)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==================== 文件上传配置 ====================

MAX_CONTENT_LENGTH = 1024 * 1024 * 1024  # 1GB 最大上传
ALLOWED_EXTENSIONS = None  # None 表示允许所有文件类型

# 允许的文件扩展名示例 (取消注释启用):
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}

# 临时上传目录
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== 权限级别 ====================

PERMISSION_READ = 'read'
PERMISSION_WRITE = 'write'
PERMISSION_ADMIN = 'admin'

# ==================== 日志配置 ====================

LOG_FILE = os.path.join(BASE_DIR, 'audit.log')
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 审计日志保留策略
AUDIT_LOG_MAX_RECORDS = 10000  # 最多保留 10000 条记录
AUDIT_LOG_MAX_AGE_DAYS = 90    # 最多保留 90 天的日志

# ==================== 速率限制 ====================

RATELIMIT_ENABLED = True
RATELIMIT_DEFAULT = "100 per hour"  # 默认限制
RATELIMIT_STORAGE_URL = "memory://"  # 内存存储，生产环境可用 "redis://localhost:6379/0"

# ==================== 管理员默认账户 ====================

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'Admin@123'
DEFAULT_ADMIN_EMAIL = 'admin@system.local'

# ==================== 系统设置 ====================

SYSTEM_NAME = 'FileHub'
SYSTEM_VERSION = '1.0.0'
SYSTEM_DESCRIPTION = '多用户文件管理系统'

# ==================== 功能开关 ====================

FEATURE_USER_REGISTRATION = False  # 是否允许用户自主注册
FEATURE_PUBLIC_SHARE = True        # 是否允许公开分享
FEATURE_TRASH = True               # 是否启用回收站
FEATURE_AUDIT_LOG = True           # 是否启用审计日志

# ==================== 生产环境检查 ====================

def is_production():
    """检查是否为生产环境"""
    return os.environ.get('FLASK_ENV') == 'production'

def check_production_config():
    """生产环境配置检查"""
    if is_production():
        warnings = []
        if SECRET_KEY == 'dev-secret-key-change-in-production-2026':
            warnings.append('⚠️  SECRET_KEY 使用默认值，生产环境必须修改！')
        if not SESSION_COOKIE_SECURE:
            warnings.append('⚠️  SESSION_COOKIE_SECURE 应为 True (HTTPS)')
        if DATABASE_PATH.startswith(BASE_DIR):
            warnings.append('⚠️  数据库文件在应用目录内，建议移到外部')
        
        if warnings:
            print('\n'.join(warnings))
            print('⚠️  请检查生产环境配置！\n')
