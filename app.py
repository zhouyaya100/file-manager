"""
File Manager - 多用户文件管理系统
主应用入口
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, send_from_directory
from functools import wraps
import os
from datetime import datetime

import config
from database import init_db, get_session, User, Permission, AuditLog, RegisteredPath
from auth import (
    authenticate_user, create_user, update_user, delete_user,
    get_user_by_id, get_all_users, login_required, admin_required,
    log_action, get_audit_logs
)
from permissions import (
    get_user_permissions, check_permission, grant_permission,
    revoke_permission, get_directory_users, get_user_accessible_directories,
    create_user_directory, validate_path_access
)
from file_manager import (
    list_files, upload_file, download_file, delete_item,
    create_directory, rename_item, get_file_info, allowed_file
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['PERMANENT_SESSION_LIFETIME'] = config.PERMANENT_SESSION_LIFETIME


# ==================== 辅助函数 ====================

@app.template_test('directory_exists')
def is_directory_exists(path):
    """Jinja2 模板测试：检查目录是否存在"""
    return os.path.isdir(path) if path else False


@app.route('/favicon.ico')
def favicon():
    """返回空 favicon，避免 500 错误"""
    return '', 204


def resolve_user_path(user_id, full_path):
    """
    解析用户请求的完整路径，返回授权的 directory_path 和 relative_path
    返回 (success, directory_path, relative_path) 或 (False, None, error_message)
    """
    if not full_path:
        return False, None, '未指定目录路径'
    
    # 获取用户的授权目录列表
    accessible_dirs = get_user_accessible_directories(user_id)
    
    # 找到匹配的授权目录（完整路径或授权目录的子目录）
    full_path_norm = os.path.normpath(full_path)
    
    for acc_dir_info in accessible_dirs:
        # acc_dir_info 是字典：{'path': ..., 'name': ..., 'level': ...}
        acc_dir = acc_dir_info['path']
        acc_dir_norm = os.path.normpath(acc_dir)
        
        if full_path_norm == acc_dir_norm:
            # 完全匹配
            return True, acc_dir, ''
        elif full_path_norm.startswith(acc_dir_norm + os.sep):
            # 子目录
            relative = full_path_norm[len(acc_dir_norm)+1:]
            return True, acc_dir, relative
    
    return False, None, '没有访问权限'


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='页面不存在', code=404), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error='权限不足', code=403), 403


@app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('error.html', error='文件太大！最大允许上传 1GB 的文件', code=413), 413


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='服务器内部错误', code=500), 500


# ==================== 认证路由 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next', url_for('dashboard'))
        
        if not username or not password:
            flash('请输入用户名和密码', 'warning')
            return render_template('login.html')
        
        user, error = authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_url or url_for('dashboard'))
        else:
            flash(error or '登录失败', 'danger')
    
    return render_template('login.html', next=request.args.get('next', ''))


@app.route('/logout')
@login_required
def logout():
    log_action(session['user_id'], session['username'], 'logout', '用户登出')
    session.clear()
    flash('已安全登出', 'info')
    return redirect(url_for('login'))


# ==================== 仪表板 ====================

@app.route('/')
@login_required
def dashboard():
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    # 获取用户的目录权限
    permissions = get_user_permissions(user_id)
    
    # 获取最近的审计日志
    recent_logs = get_audit_logs(user_id=user_id, limit=5)
    
    return render_template('dashboard.html', 
                         user=user, 
                         permissions=permissions,
                         recent_logs=recent_logs)


# ==================== 文件管理 ====================

@app.route('/files')
@login_required
def files():
    user_id = session['user_id']
    permissions = get_user_permissions(user_id)
    
    # 如果没有权限，提示
    if not permissions:
        flash('您还没有任何目录的访问权限，请联系管理员', 'warning')
    
    return render_template('files.html', permissions=permissions)


@app.route('/api/files/list')
@login_required
def api_files_list():
    user_id = session['user_id']
    full_path = request.args.get('path', '')
    
    success, directory_path, error_or_relative = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': error_or_relative}), 403
    
    relative_path = error_or_relative
    success, result = list_files(user_id, directory_path, relative_path)
    
    if success:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False, 'error': result}), 403


@app.route('/api/files/upload', methods=['POST'])
@login_required
def api_files_upload():
    user_id = session['user_id']
    full_path = request.form.get('path', '')
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400
    
    success, directory_path, error_or_relative = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': error_or_relative}), 403
    
    relative_path = error_or_relative
    success, result = upload_file(user_id, directory_path, file, relative_path)
    
    if success:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'success': False, 'error': result}), 403


@app.route('/api/files/download')
@login_required
def api_files_download():
    user_id = session['user_id']
    full_path = request.args.get('path', '')
    
    success, directory_path, relative_path = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': directory_path}), 403
    
    success, result = download_file(user_id, directory_path, relative_path)
    
    if success:
        return send_file(result, as_attachment=True)
    else:
        return jsonify({'success': False, 'error': result}), 403


@app.route('/api/files/delete', methods=['POST'])
@login_required
def api_files_delete():
    user_id = session['user_id']
    full_path = request.json.get('path', '')
    
    success, directory_path, relative_path = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': directory_path}), 403
    
    success, error = delete_item(user_id, directory_path, relative_path)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 403


@app.route('/api/files/mkdir', methods=['POST'])
@login_required
def api_files_mkdir():
    user_id = session['user_id']
    full_path = request.json.get('path', '')
    new_dir_name = request.json.get('name', '')
    
    if not full_path or not new_dir_name:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    success, directory_path, relative_path = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': directory_path}), 403
    
    success, error = create_directory(user_id, directory_path, relative_path, new_dir_name)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 403


@app.route('/api/files/rename', methods=['POST'])
@login_required
def api_files_rename():
    user_id = session['user_id']
    full_path = request.json.get('path', '')
    new_name = request.json.get('new_name', '')
    
    if not full_path or not new_name:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    success, directory_path, relative_path = resolve_user_path(user_id, full_path)
    
    if not success:
        return jsonify({'success': False, 'error': directory_path}), 403
    
    success, error = rename_item(user_id, directory_path, relative_path, new_name)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 403


# ==================== 后台管理 ====================

@app.route('/admin')
@login_required
@admin_required
def admin():
    return redirect(url_for('admin_users'))


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = get_all_users()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def admin_users_create():
    username = request.json.get('username', '').strip()
    password = request.json.get('password', '')
    email = request.json.get('email', '').strip()
    role = request.json.get('role', 'user')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码必填'}), 400
    
    user, error = create_user(username, password, email, role)
    
    if user:
        # 为用户创建默认目录
        user_dir, _ = create_user_directory(username)
        if user_dir:
            # 授予用户对自己目录的写权限
            grant_permission(user.id, user_dir, f'{username} 的目录', 'write', session['user_id'])
        
        return jsonify({'success': True, 'user': user.to_dict()})
    else:
        return jsonify({'success': False, 'error': error or '创建失败'}), 400


@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_users_toggle(user_id):
    # 防止禁用自己
    if user_id == session['user_id']:
        return jsonify({'success': False, 'error': '不能禁用自己'}), 400
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    
    # 防止禁用最后一个管理员
    if not user.is_active:
        # 检查是否是最后一个活跃管理员
        all_users = get_all_users()
        active_admins = [u for u in all_users if u.role == 'admin' and u.is_active and u.id != user_id]
        if len(active_admins) == 0:
            return jsonify({'success': False, 'error': '不能禁用最后一个管理员'}), 400
    
    success, error = update_user(user_id, is_active=not user.is_active)
    
    if success:
        log_action('admin_toggle_user', f'切换用户 {user.username} 状态为 {"启用" if not user.is_active else "禁用"}')
        return jsonify({'success': True, 'is_active': not user.is_active})
    else:
        return jsonify({'success': False, 'error': error}), 400


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_users_delete(user_id):
    if user_id == session['user_id']:
        return jsonify({'success': False, 'error': '不能删除自己'}), 400
    
    success, error = delete_user(user_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': error}), 400


@app.route('/admin/permissions')
@login_required
@admin_required
def admin_permissions():
    from sqlalchemy import func
    import os
    users = get_all_users()
    
    # 获取所有已注册的路径（从 RegisteredPath 表）
    db = get_session()
    try:
        paths_query = db.query(RegisteredPath).all()
        
        registered_paths = []
        seen_paths = set()
        
        # 添加已注册路径
        for p in paths_query:
            if p.path not in seen_paths:
                registered_paths.append({
                    'path': p.path,
                    'name': p.name or p.path
                })
                seen_paths.add(p.path)
        
        # 个人目录不需要显示在权限管理中（用户自动拥有访问权）
        # 这里只显示手动注册的共享目录
    finally:
        db.close()
    
    return render_template('admin/permissions.html', users=users, registered_paths=registered_paths)


@app.route('/admin/permissions/user/<int:user_id>')
@login_required
@admin_required
def admin_permissions_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin_permissions'))
    
    permissions = get_user_permissions(user_id)
    return render_template('admin/permissions_detail.html', user=user, permissions=permissions)


@app.route('/admin/permissions/user/<int:user_id>/api')
@login_required
@admin_required
def admin_permissions_user_api(user_id):
    """获取用户权限列表（API）"""
    try:
        permissions = get_user_permissions(user_id)
        # 转换为字典列表
        perm_list = [p.to_dict() for p in permissions]
        return jsonify({'success': True, 'permissions': perm_list})
    except Exception as e:
        import traceback
        print(f'API 错误：{traceback.format_exc()}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/permissions/grant', methods=['POST'])
@login_required
@admin_required
def admin_permissions_grant():
    user_id = request.json.get('user_id')
    directory_path = request.json.get('directory_path', '').strip()
    directory_name = request.json.get('directory_name', '').strip()
    permission_level = request.json.get('permission_level', 'read')
    action = request.json.get('action', 'grant')  # 'grant' or 'revoke'
    
    if not user_id or not directory_path:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    db = get_session()
    try:
        # 检查是否已存在授权
        existing = db.query(Permission).filter(
            Permission.user_id == user_id,
            Permission.directory_path == directory_path
        ).first()
        
        if action == 'revoke':
            # 解除授权
            if existing:
                db.delete(existing)
                db.commit()
                return jsonify({'success': True, 'action': 'revoked'})
            else:
                return jsonify({'success': False, 'error': '未找到授权记录'}), 404
        elif existing:
            # 已存在授权，更新权限级别
            if existing.permission_level != permission_level:
                existing.permission_level = permission_level
                db.commit()
                return jsonify({'success': True, 'action': 'updated'})
            else:
                return jsonify({'success': False, 'error': '权限级别未变化'}), 400
        else:
            # 授权
            if not directory_name:
                # 尝试从已注册路径中获取名称
                registered_path = db.query(RegisteredPath).filter(
                    RegisteredPath.path == directory_path
                ).first()
                if registered_path:
                    directory_name = registered_path.name
                else:
                    return jsonify({'success': False, 'error': '目录名称不能为空'}), 400
            
            if permission_level not in ['read', 'write']:
                return jsonify({'success': False, 'error': '无效的权限级别'}), 400
            
            # 检查目录是否存在
            if not os.path.exists(directory_path):
                try:
                    os.makedirs(directory_path, exist_ok=True)
                except Exception as e:
                    return jsonify({'success': False, 'error': f'无法创建目录：{e}'}), 400
            
            success, error = grant_permission(user_id, directory_path, directory_name, 
                                               permission_level, session['user_id'])
            
            if success:
                return jsonify({'success': True, 'action': 'granted'})
            else:
                return jsonify({'success': False, 'error': error}), 400
    finally:
        db.close()


@app.route('/admin/permissions/revoke', methods=['POST'])
@login_required
@admin_required
def admin_permissions_revoke():
    user_id = request.json.get('user_id')
    directory_path = request.json.get('directory_path')
    
    if not user_id or not directory_path:
        return jsonify({'success': False, 'error': '参数不完整'}), 400
    
    db = get_session()
    try:
        perm = db.query(Permission).filter(
            Permission.user_id == user_id,
            Permission.directory_path == directory_path
        ).first()
        
        if not perm:
            return jsonify({'success': False, 'error': '权限不存在'}), 404
        
        success, error = revoke_permission(user_id, perm.directory_path)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': error}), 400
    finally:
        db.close()


@app.route('/admin/paths')
@login_required
@admin_required
def admin_paths():
    """路径管理页面"""
    from sqlalchemy import func
    db = get_session()
    try:
        # 从 RegisteredPath 表获取所有已注册路径
        registered = db.query(RegisteredPath).all()
        
        # 关联查询每个路径的用户数和用户名列表
        paths = []
        for rp in registered:
            user_count = db.query(func.count(Permission.id)).filter(
                Permission.directory_path == rp.path
            ).scalar()
            
            # 获取用户名列表（用于 tooltip 显示）
            perms = db.query(Permission, User).join(
                User, Permission.user_id == User.id
            ).filter(
                Permission.directory_path == rp.path
            ).all()
            user_names = [p[1].username for p in perms] if perms else []
            
            paths.append({
                'path': rp.path,
                'name': rp.name,
                'user_count': user_count,
                'user_names': user_names,
                'created_at': rp.created_at
            })
        
        users = get_all_users()
        return render_template('admin/paths.html', paths=paths, users=users)
    finally:
        db.close()


@app.route('/admin/paths/add', methods=['POST'])
@login_required
@admin_required
def admin_paths_add():
    """添加新路径（预注册）"""
    path = request.json.get('path', '').strip()
    name = request.json.get('name', '').strip()
    
    if not path or not name:
        return jsonify({'success': False, 'error': '路径和名称不能为空'}), 400
    
    # 检查目录是否存在，不存在则创建
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            return jsonify({'success': False, 'error': f'无法创建目录：{e}'}), 400
    
    db = get_session()
    try:
        # 检查是否已存在
        existing = db.query(RegisteredPath).filter(RegisteredPath.path == path).first()
        if existing:
            return jsonify({'success': False, 'error': '此路径已注册'}), 400
        
        # 添加到 RegisteredPath 表
        rp = RegisteredPath(
            path=path,
            name=name,
            created_by=session.get('user_id')
        )
        db.add(rp)
        db.commit()
        
        log_action('路径预注册', f'管理员预注册路径：{path} ({name})', 'admin', request)
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/admin/paths/delete', methods=['POST'])
@login_required
@admin_required
def admin_paths_delete():
    """删除路径（仅从列表移除，不影响已分配权限）"""
    path = request.json.get('path', '').strip()
    
    if not path:
        return jsonify({'success': False, 'error': '路径不能为空'}), 400
    
    db = get_session()
    try:
        db.query(RegisteredPath).filter(RegisteredPath.path == path).delete()
        db.commit()
        log_action('路径删除', f'管理员删除路径列表项：{path}', 'admin', request)
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/admin/paths/users')
@login_required
@admin_required
def admin_paths_users():
    """查看路径已分配的用户"""
    path = request.args.get('path', '').strip()
    
    if not path:
        return jsonify({'success': False, 'error': '路径不能为空'}), 400
    
    db = get_session()
    try:
        perms = db.query(Permission, User).join(
            User, Permission.user_id == User.id
        ).filter(Permission.directory_path == path).all()
        
        users = []
        for perm, user in perms:
            users.append({
                'username': user.username,
                'permission_level': perm.permission_level
            })
        
        return jsonify({'users': users, 'count': len(users)})
    finally:
        db.close()


@app.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    db = get_session()
    try:
        total = db.query(AuditLog).count()
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc())\
            .offset((page - 1) * per_page).limit(per_page).all()
        return render_template('admin/logs.html', logs=logs, page=page, total=total, per_page=per_page)
    finally:
        db.close()


@app.route('/admin/directories')
@login_required
@admin_required
def admin_directories():
    """管理所有共享目录"""
    db = get_session()
    try:
        # 获取所有不同的目录路径
        perms = db.query(Permission.directory_path, Permission.directory_name).distinct().all()
        directories = [{'path': p.directory_path, 'name': p.directory_name} for p in perms]
        return render_template('admin/directories.html', directories=directories)
    finally:
        db.close()


@app.route('/admin/logs/delete', methods=['POST'])
@login_required
@admin_required
def admin_logs_delete():
    """删除审计日志（支持单条和批量删除）"""
    db = get_session()
    try:
        data = request.json
        log_ids = data.get('log_ids', [])
        
        if not log_ids:
            return jsonify({'success': False, 'error': '未指定要删除的日志'}), 400
        
        # 删除指定的日志
        deleted_count = db.query(AuditLog).filter(AuditLog.id.in_(log_ids)).delete(synchronize_session=False)
        db.commit()
        
        # 记录删除操作
        current_user = get_user_by_id(session['user_id'])
        log_action(session['user_id'], current_user.username, 'delete_logs', 
                   f'删除了 {deleted_count} 条审计日志', status='success')
        
        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/admin/logs/clear-all', methods=['POST'])
@login_required
@admin_required
def admin_logs_clear_all():
    """清空所有审计日志（危险操作）"""
    db = get_session()
    try:
        # 统计要删除的数量
        total_count = db.query(AuditLog).count()
        
        if total_count == 0:
            return jsonify({'success': False, 'error': '没有日志可删除'}), 400
        
        # 删除所有日志
        db.query(AuditLog).delete(synchronize_session=False)
        db.commit()
        
        # 记录删除操作
        current_user = get_user_by_id(session['user_id'])
        log_action(session['user_id'], current_user.username, 'clear_logs', 
                   f'清空了所有 {total_count} 条审计日志', status='success')
        
        return jsonify({'success': True, 'deleted_count': total_count})
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


# ==================== 用户设置 ====================

@app.route('/settings/profile')
@login_required
def settings_profile():
    """个人资料设置"""
    user = get_user_by_id(session['user_id'])
    return render_template('settings/profile.html', user=user)


@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """修改密码（用户修改自己的密码）"""
    db = get_session()
    try:
        # 检查是否有 JSON 数据
        if not request.is_json:
            return jsonify({'success': False, 'error': '请求格式错误，请使用 JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的 JSON 数据'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # 验证输入
        if not current_password:
            return jsonify({'success': False, 'error': '请输入当前密码'}), 400
        
        if not new_password:
            return jsonify({'success': False, 'error': '请输入新密码'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': '密码长度至少 6 位'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': '两次输入的密码不一致'}), 400
        
        # 获取当前用户
        user = db.query(User).filter(User.id == session['user_id']).first()
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        # 验证当前密码
        from auth import verify_password, hash_password
        if not verify_password(user.password_hash, current_password):
            return jsonify({'success': False, 'error': '当前密码错误'}), 400
        
        # 更新密码
        user.password_hash = hash_password(new_password)
        db.commit()
        
        # 记录日志
        log_action(session['user_id'], user.username, 'change_password', '修改密码成功', status='success')
        
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.rollback()
        print(f'[ERROR change-password] {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def admin_reset_password(user_id):
    """管理员重置其他用户的密码"""
    db = get_session()
    try:
        if not request.is_json:
            return jsonify({'success': False, 'error': '请求格式错误'}), 400
        
        data = request.get_json()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # 验证输入
        if not new_password:
            return jsonify({'success': False, 'error': '请输入新密码'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'error': '密码长度至少 6 位'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'error': '两次输入的密码不一致'}), 400
        
        # 获取目标用户
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            return jsonify({'success': False, 'error': '用户不存在'}), 404
        
        # 不能重置自己的密码（用自己的修改密码功能）
        if target_user.id == session['user_id']:
            return jsonify({'success': False, 'error': '请使用个人设置中的修改密码功能'}), 400
        
        from auth import hash_password
        # 更新密码
        target_user.password_hash = hash_password(new_password)
        db.commit()
        
        # 记录日志
        current_user = get_user_by_id(session['user_id'])
        log_action(session['user_id'], current_user.username, 'reset_user_password', 
                   f'重置用户 {target_user.username} 的密码', status='success')
        
        return jsonify({'success': True, 'message': f'用户 {target_user.username} 密码已重置'})
    except Exception as e:
        db.rollback()
        print(f'[ERROR reset-password] {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()


# ==================== API 工具 ====================

@app.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """获取系统统计信息"""
    db = get_session()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_permissions = db.query(Permission).count()
        total_logs = db.query(AuditLog).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'total_permissions': total_permissions,
            'total_logs': total_logs
        })
    finally:
        db.close()


# ==================== 初始化 ====================

def create_default_admin():
    """创建默认管理员账户"""
    admin = get_session().query(User).filter(User.role == 'admin').first()
    if not admin:
        user, _ = create_user('admin', 'Admin@123', 'admin@system.local', 'admin')
        if user:
            print(f'[OK] 创建默认管理员：admin / Admin@123')


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print('[OK] 数据库初始化完成')
    
    # 创建默认管理员
    create_default_admin()
    
    # 创建数据目录
    os.makedirs(config.DATA_ROOT, exist_ok=True)
    print(f'[OK] 数据目录：{config.DATA_ROOT}')
    
    # 配置日志
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # 启动服务
    print('\n>>> 启动文件管理系统...')
    print('>>> 访问地址：http://localhost:5000')
    print('>>> 生产环境请使用 Gunicorn + Nginx\n')
    
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
