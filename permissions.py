"""
权限管理模块
"""
import os
from database import get_session, User, Permission
from auth import log_action
from datetime import datetime


def get_user_permissions(user_id):
    """获取用户的所有目录权限"""
    db = get_session()
    try:
        return db.query(Permission).filter(Permission.user_id == user_id).all()
    finally:
        db.close()


def check_permission(user_id, directory_path, required_level='read'):
    """
    检查用户是否有指定目录的权限
    required_level: 'read' 或 'write'
    """
    db = get_session()
    try:
        # 规范化路径以处理斜杠差异（/ vs \）和大小写
        normalized_path = os.path.normpath(directory_path).lower()
        
        perms = db.query(Permission).filter(
            Permission.user_id == user_id
        ).all()
        
        for perm in perms:
            # 规范化数据库中存储的路径
            perm_path = os.path.normpath(perm.directory_path).lower()
            
            # 精确匹配或子目录匹配
            if perm_path == normalized_path or normalized_path.startswith(perm_path + os.sep):
                # write 权限包含 read 权限
                if required_level == 'read':
                    return perm.permission_level in ['read', 'write']
                elif required_level == 'write':
                    return perm.permission_level == 'write'
        
        return False
    finally:
        db.close()


def grant_permission(user_id, directory_path, directory_name, permission_level, granted_by=None):
    """
    授予用户目录权限
    permission_level: 'read' 或 'write'
    """
    db = get_session()
    try:
        # 检查是否已存在权限
        existing = db.query(Permission).filter(
            Permission.user_id == user_id,
            Permission.directory_path == directory_path
        ).first()
        
        if existing:
            # 更新现有权限
            existing.permission_level = permission_level
            existing.directory_name = directory_name
            existing.granted_by = granted_by
        else:
            # 创建新权限
            perm = Permission(
                user_id=user_id,
                directory_path=directory_path,
                directory_name=directory_name,
                permission_level=permission_level,
                granted_by=granted_by
            )
            db.add(perm)
        
        db.commit()
        
        # 获取用户名用于日志
        user_db = get_session()
        user = user_db.query(User).filter(User.id == user_id).first()
        username = user.username if user else str(user_id)
        user_db.close()
        
        # 记录日志
        log_action(granted_by, 'system', 'grant_permission', 
                   f'授予 {username} 权限：{permission_level} - {directory_name}',
                   target_path=directory_path)
        
        return True, None
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def revoke_permission(user_id, directory_path):
    """撤销用户的目录权限"""
    db = get_session()
    try:
        perm = db.query(Permission).filter(
            Permission.user_id == user_id,
            Permission.directory_path == directory_path
        ).first()
        
        if not perm:
            return False, '权限不存在'
        
        # 获取用户名用于日志
        user_db = get_session()
        user = user_db.query(User).filter(User.id == user_id).first()
        username = user.username if user else str(user_id)
        user_db.close()
        
        db.delete(perm)
        db.commit()
        
        # 记录日志
        log_action(None, 'system', 'revoke_permission',
                   f'撤销 {username} 权限：{directory_path}',
                   target_path=directory_path)
        
        return True, None
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_directory_users(directory_path):
    """获取有指定目录权限的所有用户"""
    db = get_session()
    try:
        perms = db.query(Permission).filter(
            Permission.directory_path == directory_path
        ).all()
        
        result = []
        for perm in perms:
            user = db.query(User).filter(User.id == perm.user_id).first()
            if user:
                result.append({
                    'user': user,
                    'permission': perm
                })
        return result
    finally:
        db.close()


def get_user_accessible_directories(user_id):
    """获取用户可访问的所有目录"""
    db = get_session()
    try:
        perms = db.query(Permission).filter(Permission.user_id == user_id).all()
        return [{'path': p.directory_path, 'name': p.directory_name, 'level': p.permission_level} 
                for p in perms]
    finally:
        db.close()


def create_user_directory(username, base_path=None):
    """
    为用户创建专属目录
    同时设置 Linux 文件系统权限（在 Ubuntu 上）
    """
    import config
    
    if base_path is None:
        base_path = config.DATA_ROOT
    
    user_dir = os.path.join(base_path, username)
    
    try:
        # 创建目录
        os.makedirs(user_dir, exist_ok=True)
        
        # 在 Ubuntu 上设置目录权限
        # 注意：这在 Windows 上不会生效，但在 Ubuntu 部署时会工作
        try:
            os.chmod(user_dir, 0o755)  # rwxr-xr-x
        except:
            pass  # Windows 上忽略权限设置
        
        return user_dir, None
    except Exception as e:
        return None, str(e)


def validate_path_access(user_id, requested_path):
    """
    验证用户是否有权访问指定路径
    返回 (is_valid, actual_path, permission_level)
    """
    db = get_session()
    try:
        perms = db.query(Permission).filter(Permission.user_id == user_id).all()
        
        for perm in perms:
            # 检查路径是否以授权目录开头
            normalized_requested = os.path.normpath(requested_path)
            normalized_perm = os.path.normpath(perm.directory_path)
            
            if normalized_requested == normalized_perm or \
               normalized_requested.startswith(normalized_perm + os.sep):
                return True, normalized_requested, perm.permission_level
        
        return False, None, None
    finally:
        db.close()
