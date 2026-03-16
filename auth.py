"""
用户认证模块
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_session, User, AuditLog
from datetime import datetime
import config


def hash_password(password):
    """密码加密"""
    return generate_password_hash(password, method='pbkdf2:sha256:260000')


def verify_password(password_hash, password):
    """验证密码"""
    return check_password_hash(password_hash, password)


def create_user(username, password, email=None, role='user', is_active=True):
    """创建用户"""
    db = get_session()
    try:
        # 检查用户名是否已存在
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return None, '用户名已存在'
        
        # 如果邮箱为空，生成唯一邮箱地址
        if not email or email.strip() == '':
            import time
            email = f'{username}_{int(time.time())}@system.local'
        else:
            # 检查邮箱是否已被使用
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:
                return None, '邮箱已被使用'
        
        # 创建新用户
        user = User(
            username=username,
            password_hash=hash_password(password),
            email=email,
            role=role,
            is_active=is_active
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 记录日志
        log_action(user.id, username, 'create_user', f'创建用户：{username}')
        
        return user, None
    except Exception as e:
        db.rollback()
        return None, str(e)
    finally:
        db.close()


def authenticate_user(username, password):
    """用户认证"""
    db = get_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            log_action(None, username, 'login_failed', '用户不存在', status='failed')
            return None, '用户名或密码错误'
        
        if not user.is_active:
            log_action(user.id, username, 'login_failed', '用户已禁用', status='failed')
            return None, '账户已被禁用'
        
        if not verify_password(user.password_hash, password):
            log_action(user.id, username, 'login_failed', '密码错误', status='failed')
            return None, '用户名或密码错误'
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        db.commit()
        
        # 记录登录日志
        log_action(user.id, username, 'login', '用户登录成功')
        
        return user, None
    except Exception as e:
        db.rollback()
        return None, str(e)
    finally:
        db.close()


def get_user_by_id(user_id):
    """根据 ID 获取用户"""
    db = get_session()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_user_by_username(username):
    """根据用户名获取用户"""
    db = get_session()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


def update_user(user_id, **kwargs):
    """更新用户信息"""
    db = get_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, '用户不存在'
        
        # 更新允许的字段
        allowed_fields = ['email', 'role', 'is_active']
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        # 如果修改密码
        if 'password' in kwargs and kwargs['password']:
            user.password_hash = hash_password(kwargs['password'])
        
        db.commit()
        
        # 记录日志
        log_action(user_id, user.username, 'update_user', f'更新用户信息：{kwargs.keys()}')
        
        return True, None
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def delete_user(user_id):
    """删除用户"""
    db = get_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, '用户不存在'
        
        username = user.username
        db.delete(user)
        db.commit()
        
        # 记录日志
        log_action(None, username, 'delete_user', f'删除用户：{username}')
        
        return True, None
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_all_users():
    """获取所有用户"""
    db = get_session()
    try:
        return db.query(User).order_by(User.created_at.desc()).all()
    finally:
        db.close()


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 检查是否为 API 请求
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': '请先登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 检查是否为 API 请求
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': '未登录'}), 401
            flash('请先登录', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user = get_user_by_id(session['user_id'])
        if not user or user.role != 'admin' or not user.is_active:
            # 检查是否为 API 请求
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': '权限不足'}), 403
            flash('权限不足', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def log_action(user_id, username, action, details=None, target_path=None, status='success'):
    """记录审计日志"""
    db = get_session()
    try:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            target_path=target_path,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            status=status,
            details=details
        )
        db.add(log)
        db.commit()
        
        # 定期清理旧日志（每 100 次操作清理一次）
        _cleanup_old_logs(db)
    except Exception as e:
        db.rollback()
        print(f'记录日志失败：{e}')
    finally:
        db.close()


def _cleanup_old_logs(db):
    """清理旧的审计日志，防止数据库无限增长"""
    import config
    from datetime import timedelta
    
    try:
        # 检查日志总数
        total_count = db.query(AuditLog).count()
        
        # 只有在接近限制时才清理
        if total_count > config.AUDIT_LOG_MAX_RECORDS * 0.9:
            # 按时间排序，删除最旧的记录，保留最新的 N 条
            old_logs = db.query(AuditLog).order_by(AuditLog.timestamp.asc()) \
                .limit(total_count - config.AUDIT_LOG_MAX_RECORDS + 100).all()
            
            for log in old_logs:
                db.delete(log)
            
            db.commit()
            print(f'[日志清理] 已清理 {len(old_logs)} 条旧日志，当前保留 {config.AUDIT_LOG_MAX_RECORDS} 条')
        
        # 同时清理超过年龄的日志
        cutoff_date = datetime.now() - timedelta(days=config.AUDIT_LOG_MAX_AGE_DAYS)
        old_by_age = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).all()
        
        if old_by_age:
            for log in old_by_age:
                db.delete(log)
            db.commit()
            print(f'[日志清理] 已清理 {len(old_by_age)} 条超过 {config.AUDIT_LOG_MAX_AGE_DAYS} 天的日志')
    except Exception as e:
        db.rollback()
        print(f'日志清理失败：{e}')


def get_audit_logs(user_id=None, limit=100):
    """获取审计日志"""
    db = get_session()
    try:
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    finally:
        db.close()
