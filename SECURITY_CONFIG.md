# 安全配置指南

多用户文件管理系统 v1.0.0 安全配置详细说明。

---

## 🔐 文件上传安全配置

### 当前配置（v1.0.0）

**默认设置：允许所有文件类型上传**

```python
# config.py
ALLOWED_EXTENSIONS = None  # None = 允许所有类型
```

---

## ⚙️ 配置选项

### 选项 1：允许所有类型（当前默认）

```python
# config.py
ALLOWED_EXTENSIONS = None
```

**适用场景：**
- 内部可信用户环境
- 需要上传特殊文件格式
- 有其他安全措施（如病毒扫描）

**风险等级：** 🔴 高风险

---

### 选项 2：白名单模式（推荐）

```python
# config.py
ALLOWED_EXTENSIONS = {
    # 文档
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'odt', 'ods', 'odp', 'rtf', 'md',
    
    # 图片
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'ico',
    
    # 音频
    'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',
    
    # 视频
    'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm',
    
    # 压缩包
    'zip', 'rar', '7z', 'tar', 'gz',
    
    # 其他
    'csv', 'json', 'xml', 'yaml', 'yml'
}
```

**适用场景：**
- 生产环境
- 多用户公共环境
- 需要严格控制文件类型

**风险等级：** 🟢 低风险

---

### 选项 3：黑名单模式（部分限制）

```python
# file_manager.py
BLOCKED_EXTENSIONS = {
    # Windows 可执行文件
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
    
    # 脚本文件
    '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsc', '.wsh',
    '.ps1', '.psc1', '.pl', '.rb', '.py', '.pyc', '.pyo',
    
    # Web 脚本（防止 WebShell）
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.asp', '.aspx', '.jsp', '.jspx', '.asa', '.asax',
    
    # 系统文件
    '.dll', '.sys', '.drv', '.ocx', '.cpl',
    '.msc', '.msp', '.msi', '.inf', '.lnk',
    
    # Java
    '.jar', '.war', '.ear',
    
    # macOS
    '.app', '.dmg', '.pkg',
    
    # Linux
    '.sh', '.bash', '.zsh', '.ksh',
    '.so', '.ko'
}

def allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext not in BLOCKED_EXTENSIONS
```

**适用场景：**
- 需要大部分文件类型
- 仅阻止危险文件
- 平衡安全性和灵活性

**风险等级：** 🟡 中等风险

---

## 🛡️ 安全建议

### 生产环境推荐配置

```python
# config.py
import os

# 1. 使用白名单
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'png', 'jpg', 'jpeg', 'gif',
    'mp3', 'mp4',
    'zip', 'rar'
}

# 2. 限制文件大小
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

# 3. 设置安全密钥
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("生产环境必须设置 SECRET_KEY")

# 4. 启用 HTTPS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

---

## 📋 文件类型风险分类

### 🔴 极高风险（必须阻止）

| 类型 | 扩展名 | 风险说明 |
|------|--------|----------|
| **Windows 可执行** | .exe, .bat, .cmd, .com | 直接运行恶意代码 |
| **PowerShell 脚本** | .ps1, .psc1 | 系统级脚本执行 |
| **Web 脚本** | .php, .asp, .jsp | 上传 WebShell 控制服务器 |
| **VBScript** | .vbs, .vbe | Windows 脚本病毒 |

---

### 🟡 中等风险（建议阻止）

| 类型 | 扩展名 | 风险说明 |
|------|--------|----------|
| **Python 脚本** | .py, .pyc | 可能包含恶意代码 |
| **Java 归档** | .jar, .war | 可能包含恶意类 |
| **系统文件** | .dll, .sys, .drv | 可能被利用 |
| **快捷方式** | .lnk, .scf | 社会工程学攻击 |

---

### 🟢 低风险（通常安全）

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| **文档** | .doc, .pdf, .txt | 办公文档 |
| **图片** | .jpg, .png, .gif | 图像文件 |
| **音频** | .mp3, .wav | 音频文件 |
| **视频** | .mp4, .avi | 视频文件 |
| **压缩包** | .zip, .rar | 压缩文件（注意内部可能包含恶意文件） |

---

## 🔧 高级安全配置

### 1. 文件内容检查（MIME 类型）

```python
# 安装依赖
# pip install python-magic

import magic

def check_file_content(file_stream):
    """检查文件真实类型（防止扩展名伪装）"""
    mime = magic.from_buffer(file_stream.read(1024), mime=True)
    file_stream.seek(0)  # 重置指针
    
    # 阻止可执行文件 MIME 类型
    dangerous_mime = [
        'application/x-executable',
        'application/x-dosexec',
        'application/x-msdownload',
        'text/x-python',
        'application/x-php',
        'application/x-shellscript'
    ]
    
    return mime not in dangerous_mime
```

---

### 2. 病毒扫描集成

```python
# 安装 ClamAV
# sudo apt install clamav-daemon
# pip install python-clamd

import clamd

def scan_file_for_virus(file_path):
    """使用 ClamAV 扫描文件"""
    try:
        cd = clamd.ClamdUnixSocket()
        result = cd.scan(file_path)
        
        if result['stream'][0] == 'OK':
            return True, "文件安全"
        else:
            return False, f"检测到病毒：{result['stream'][1]}"
    except Exception as e:
        return True, f"扫描失败：{str(e)}"  # 扫描失败时默认允许
```

---

### 3. 文件隔离存储

```python
# config.py
UPLOAD_ROOT = 'data/uploads'

# 不同类型文件存储到不同目录
UPLOAD_DIRS = {
    'safe': os.path.join(UPLOAD_ROOT, 'safe'),      # 文档/图片
    'archive': os.path.join(UPLOAD_ROOT, 'archive'), # 压缩包
    'quarantine': os.path.join(UPLOAD_ROOT, 'quarantine')  # 可疑文件
}

# Nginx 配置：禁止直接访问 quarantine 目录
# location /uploads/quarantine { deny all; }
```

---

### 4. 上传审计和告警

```python
# app.py
DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.ps1', '.php', '.sh'}

def log_upload(filename, user_id):
    """记录上传日志，危险文件触发告警"""
    _, ext = os.path.splitext(filename.lower())
    
    log_audit('file_upload', filename, 'success')
    
    # 危险文件上传告警
    if ext in DANGEROUS_EXTENSIONS:
        log_audit('dangerous_file_upload', filename, 'warning')
        # 可发送邮件/短信告警
        # send_alert(f"用户 {user_id} 上传了危险文件：{filename}")
```

---

## 📊 配置对比

| 配置模式 | 安全性 | 灵活性 | 适用场景 |
|----------|--------|--------|----------|
| **白名单** | ⭐⭐⭐⭐⭐ | ⭐⭐ | 生产环境、公共系统 |
| **黑名单** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 内部可信用户 |
| **全开放** | ⭐ | ⭐⭐⭐⭐⭐ | 测试环境、单人使用 |

---

## ✅ 安全检查清单

### 上线前配置

- [ ] 设置 `ALLOWED_EXTENSIONS` 白名单
- [ ] 限制 `MAX_CONTENT_LENGTH` 文件大小
- [ ] 设置强 `SECRET_KEY`
- [ ] 启用 HTTPS
- [ ] 配置安全响应头
- [ ] 设置文件目录权限

### 运行中监控

- [ ] 定期检查审计日志
- [ ] 监控异常上传行为
- [ ] 定期扫描上传文件
- [ ] 更新文件类型黑名单

---

## 📝 配置示例

### 示例 1：企业办公环境

```python
# config.py
ALLOWED_EXTENSIONS = {
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'pdf', 'txt', 'rtf',
    'png', 'jpg', 'jpeg', 'gif',
    'zip', 'rar'
}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
```

---

### 示例 2：设计公司

```python
# config.py
ALLOWED_EXTENSIONS = {
    # 设计文件
    'psd', 'ai', 'sketch', 'fig', 'xd',
    'afdesign', 'afphoto',
    
    # 图片
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'tiff',
    
    # 视频
    'mp4', 'mov', 'avi', 'mkv',
    
    # 文档
    'pdf', 'doc', 'docx', 'txt'
}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
```

---

### 示例 3：开发团队

```python
# config.py
ALLOWED_EXTENSIONS = {
    # 代码文件
    'py', 'js', 'ts', 'java', 'cpp', 'c', 'h', 'hpp',
    'go', 'rs', 'rb', 'php', 'swift', 'kt',
    
    # 配置文件
    'json', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf',
    'xml', 'md', 'rst',
    
    # 压缩包
    'zip', 'rar', 'tar', 'gz', '7z'
}
# 注意：需要配合文件隔离存储，禁止直接执行
```

---

## 🚨 应急响应

### 发现恶意文件上传

1. **立即隔离文件**
   ```bash
   mv /path/to/uploads/malicious.exe /quarantine/
   ```

2. **删除文件**
   ```bash
   rm /quarantine/malicious.exe
   ```

3. **审计日志调查**
   - 查看谁上传的
   - 查看上传时间
   - 查看 IP 地址

4. **修改配置**
   - 添加该文件类型到黑名单
   - 加强文件类型限制

5. **通知用户**
   - 如果是误操作，教育用户
   - 如果是恶意行为，禁用账户

---

**安全第一！根据实际场景选择合适的配置！** 🔒

*最后更新：2026-03-15*
