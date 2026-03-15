"""
文件管理模块
"""
import os
import shutil
from werkzeug.utils import secure_filename
from database import get_session, User
from auth import log_action
import config
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


def allowed_file(filename):
    """
    检查文件扩展名是否允许
    
    当前配置：允许所有文件类型上传
    如需限制，可修改 config.ALLOWED_EXTENSIONS 或使用黑名单
    """
    # 配置为 None 表示允许所有文件类型
    if config.ALLOWED_EXTENSIONS is None:
        return True
    
    # 获取文件扩展名（小写）
    _, ext = os.path.splitext(filename.lower())
    ext = ext.lstrip('.')
    
    # 检查是否在允许列表中
    return ext in config.ALLOWED_EXTENSIONS


def get_safe_path(base_path, *path_parts):
    """
    构建安全的路径，防止路径遍历攻击
    """
    # 组合路径
    full_path = os.path.join(base_path, *path_parts)
    # 规范化路径
    full_path = os.path.normpath(full_path)
    # 确保路径在 base_path 内
    base_path = os.path.normpath(base_path)
    if not full_path.startswith(base_path):
        return None
    return full_path


def list_files(user_id, directory_path, relative_path=''):
    """
    列出目录内容
    返回 (success, result/error)
    """
    from permissions import check_permission
    
    # 检查权限
    if not check_permission(user_id, directory_path, 'read'):
        return False, '没有访问权限'
    
    try:
        target_path = os.path.join(directory_path, relative_path) if relative_path else directory_path
        target_path = os.path.normpath(target_path)
        
        # 确保路径在授权目录内
        if not target_path.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        if not os.path.exists(target_path):
            return False, '目录不存在'
        
        if not os.path.isdir(target_path):
            return False, '不是目录'
        
        items = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            item_relative_path = os.path.join(relative_path, item) if relative_path else item
            stat_info = os.stat(item_path)
            
            items.append({
                'name': item,
                'path': item_path,  # 返回完整路径
                'relative_path': item_relative_path,  # 同时保留相对路径
                'is_directory': os.path.isdir(item_path),
                'size': stat_info.st_size if os.path.isfile(item_path) else 0,
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime
            })
        
        # 排序：目录在前，文件在后，按名称排序
        items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
        
        # 添加父目录导航
        if relative_path:
            parent = os.path.dirname(relative_path)
            items.insert(0, {
                'name': '..',
                'path': parent if parent else '',
                'is_directory': True,
                'size': 0,
                'modified': 0,
                'created': 0,
                'is_parent': True
            })
        
        return True, {
            'current_path': target_path,  # 返回完整路径
            'directory_path': directory_path,
            'relative_path': relative_path,
            'items': items
        }
    except Exception as e:
        return False, str(e)


def upload_file(user_id, directory_path, file, relative_path=''):
    """
    上传文件
    """
    from permissions import check_permission
    
    # 检查写权限
    if not check_permission(user_id, directory_path, 'write'):
        return False, '没有写入权限'
    
    try:
        target_dir = os.path.join(directory_path, relative_path) if relative_path else directory_path
        target_dir = os.path.normpath(target_dir)
        
        # 确保路径在授权目录内
        if not target_dir.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        if not os.path.exists(target_dir):
            return False, '目录不存在'
        
        # 安全检查文件名（保留中文和原始文件名）
        original_filename = file.filename
        if not original_filename:
            return False, '无效的文件名'
        
        # 防止路径遍历攻击：只保留文件名部分
        filename = os.path.basename(original_filename)
        # 替换危险字符但保留中文和扩展名
        filename = filename.replace('\\', '_').replace('/', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        
        if not filename or filename.startswith('.'):
            return False, '无效的文件名'
        
        # 检查文件扩展名
        if not allowed_file(filename):
            return False, '不支持的文件类型'
        
        # 保存文件
        file_path = os.path.join(target_dir, filename)
        
        # 处理重名
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            filename = f'{base}_{counter}{ext}'
            file_path = os.path.join(target_dir, filename)
            counter += 1
        
        file.save(file_path)
        
        # 记录日志
        log_action(user_id, None, 'upload', f'上传文件：{filename}', target_path=file_path)
        
        return True, {'filename': filename, 'path': os.path.join(relative_path, filename)}
    except Exception as e:
        return False, str(e)


def download_file(user_id, directory_path, relative_path):
    """
    下载文件
    返回 (success, file_path/error)
    """
    from permissions import check_permission
    
    if not check_permission(user_id, directory_path, 'read'):
        return False, '没有访问权限'
    
    try:
        file_path = os.path.join(directory_path, relative_path)
        file_path = os.path.normpath(file_path)
        
        # 确保路径在授权目录内
        if not file_path.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        if not os.path.exists(file_path):
            return False, '文件不存在'
        
        if os.path.isdir(file_path):
            return False, '不能下载目录'
        
        # 记录日志
        log_action(user_id, None, 'download', f'下载文件：{relative_path}', target_path=file_path)
        
        return True, file_path
    except Exception as e:
        return False, str(e)


def delete_item(user_id, directory_path, relative_path):
    """
    删除文件或目录
    """
    from permissions import check_permission
    
    if not check_permission(user_id, directory_path, 'write'):
        return False, '没有写入权限'
    
    try:
        item_path = os.path.join(directory_path, relative_path)
        item_path = os.path.normpath(item_path)
        
        # 确保路径在授权目录内
        if not item_path.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        if not os.path.exists(item_path):
            return False, '项目不存在'
        
        item_name = os.path.basename(item_path)
        is_dir = os.path.isdir(item_path)
        
        if is_dir:
            shutil.rmtree(item_path)
            log_action(user_id, None, 'delete_directory', f'删除目录：{relative_path}', target_path=item_path)
        else:
            os.remove(item_path)
            log_action(user_id, None, 'delete', f'删除文件：{relative_path}', target_path=item_path)
        
        return True, None
    except Exception as e:
        return False, str(e)


def create_directory(user_id, directory_path, relative_path, new_dir_name):
    """
    创建新目录
    """
    from permissions import check_permission
    
    if not check_permission(user_id, directory_path, 'write'):
        return False, '没有写入权限'
    
    try:
        parent_path = os.path.join(directory_path, relative_path) if relative_path else directory_path
        parent_path = os.path.normpath(parent_path)
        
        # 确保路径在授权目录内
        if not parent_path.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        new_dir_path = os.path.join(parent_path, secure_filename(new_dir_name))
        
        if os.path.exists(new_dir_path):
            return False, '目录已存在'
        
        os.makedirs(new_dir_path, exist_ok=True)
        
        # 记录日志
        log_action(user_id, None, 'create_directory', f'创建目录：{new_dir_name}', target_path=new_dir_path)
        
        return True, None
    except Exception as e:
        return False, str(e)


def rename_item(user_id, directory_path, relative_path, new_name):
    """
    重命名文件或目录
    """
    from permissions import check_permission
    
    if not check_permission(user_id, directory_path, 'write'):
        return False, '没有写入权限'
    
    try:
        old_path = os.path.join(directory_path, relative_path)
        old_path = os.path.normpath(old_path)
        
        # 确保路径在授权目录内
        if not old_path.startswith(os.path.normpath(directory_path)):
            return False, '非法路径访问'
        
        parent = os.path.dirname(old_path)
        new_path = os.path.join(parent, secure_filename(new_name))
        
        if os.path.exists(new_path):
            return False, '目标名称已存在'
        
        os.rename(old_path, new_path)
        
        # 记录日志
        log_action(user_id, None, 'rename', f'重命名：{relative_path} -> {new_name}', target_path=old_path)
        
        return True, None
    except Exception as e:
        return False, str(e)


def get_file_info(user_id, directory_path, relative_path):
    """
    获取文件/目录详细信息
    """
    from permissions import check_permission
    
    if not check_permission(user_id, directory_path, 'read'):
        return False, '没有访问权限'
    
    try:
        item_path = os.path.join(directory_path, relative_path)
        item_path = os.path.normpath(item_path)
        
        if not os.path.exists(item_path):
            return False, '项目不存在'
        
        stat_info = os.stat(item_path)
        
        return True, {
            'name': os.path.basename(item_path),
            'path': relative_path,
            'is_directory': os.path.isdir(item_path),
            'size': stat_info.st_size if os.path.isfile(item_path) else 0,
            'modified': stat_info.st_mtime,
            'created': stat_info.st_ctime,
            'absolute_path': item_path
        }
    except Exception as e:
        return False, str(e)
