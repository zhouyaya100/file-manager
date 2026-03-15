# 多用户文件管理系统 v1.0.0

🔐 基于 Flask 的企业级多用户文件管理系统，支持细粒度目录权限控制。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](CHANGELOG.md)

**快速开始:** [安装指南](INSTALL.md) | [快速上手](QUICKSTART.md) | [更新日志](CHANGELOG.md)

## ✨ 功能特性

### 核心功能
- 🔐 **多用户支持** - 独立账户，会话管理，角色权限
- 📁 **权限控制** - 按目录分配读/写权限，支持子目录继承
- 📊 **审计日志** - 记录所有关键操作，支持查询和筛选
- 🎨 **现代 UI** - 科技感设计，响应式布局，支持移动端

### 文件操作
- 📤 **上传下载** - 支持所有文件类型，最大 1GB，断点续传（计划中）
- 🗑️ **删除管理** - 文件/目录删除，操作可追溯
- ✏️ **重命名** - 文件和目录重命名
- 📂 **目录管理** - 创建多级目录，树形导航

### 管理功能
- 👥 **用户管理** - 创建/禁用/删除用户，密码重置
- 🔑 **权限管理** - 可视化权限配置，批量授权
- 📝 **日志审计** - 完整操作日志，支持导出（计划中）

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python 3.8+ / Flask 2.3+ |
| 前端 | HTML5 / Bootstrap 5.3 / JavaScript |
| 数据库 | SQLite (可切换 PostgreSQL/MySQL) |
| 部署 | Gunicorn + Nginx (生产环境) |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd file_manager
pip install -r requirements.txt
```

### 2. 启动服务

**Windows:**
```powershell
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 3. 访问系统

浏览器打开：http://localhost:5000

**默认管理员账户:**
- 用户名：`admin`
- 密码：`Admin@123`

⚠️ **首次登录后请立即修改密码！**

### 📚 更多文档

- 📖 [安装指南](INSTALL.md) - 详细安装步骤和故障排查
- 🏃 [快速上手](QUICKSTART.md) - 5 分钟快速开始
- 📦 [发布说明](RELEASE_NOTES.md) - 功能列表和更新日志
- 🐧 [Linux 部署](DEPLOY_LINUX.md) - 生产环境部署指南
- 🤝 [贡献指南](CONTRIBUTING.md) - 如何参与项目开发

## 📁 项目结构

```
file_manager/
├── app.py                      # Flask 应用入口
├── config.py                   # 配置文件
├── database.py                 # 数据库模型
├── auth.py                     # 认证模块
├── permissions.py              # 权限管理
├── file_manager.py             # 文件操作
├── requirements.txt            # 依赖包
├── start.py                    # 启动脚本（通用）
├── start.bat                   # 启动脚本（Windows）
├── start.sh                    # 启动脚本（Linux/Mac）
│
├── templates/                  # HTML 模板
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── files.html
│   ├── error.html
│   ├── settings/
│   │   └── profile.html
│   └── admin/
│       ├── users.html
│       ├── permissions.html
│       ├── logs.html
│       └── directories.html
│
├── static/                     # 静态资源
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       └── files.js
│
└── data/                       # 数据存储（运行时创建）
    └── users/                  # 用户文件存储
```

## 配置说明

编辑 `config.py` 修改配置：

```python
SECRET_KEY = 'your-secret-key-here'  # 生产环境务必修改
DATA_ROOT = 'data/users'              # 文件存储根目录
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 最大上传 500MB
PERMANENT_SESSION_LIFETIME = 3600 * 24  # 会话有效期 24 小时
```

## 生产环境部署

详细部署指南请查看：[DEPLOY_LINUX.md](DEPLOY_LINUX.md)

### Ubuntu 快速部署

### 1. 安装系统依赖

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置 Gunicorn

创建 `gunicorn.conf.py`:

```python
bind = "127.0.0.1:5000"
workers = 4
threads = 2
worker_class = "sync"
timeout = 120
keepalive = 5
accesslog = "/var/log/file_manager/access.log"
errorlog = "/var/log/file_manager/error.log"
```

### 4. 配置 Nginx

`/etc/nginx/sites-available/file_manager`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 500M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用站点:
```bash
sudo ln -s /etc/nginx/sites-available/file_manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 创建 Systemd 服务

`/etc/systemd/system/file_manager.service`:

```ini
[Unit]
Description=File Manager Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/file_manager
ExecStart=/path/to/file_manager/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable file_manager
sudo systemctl start file_manager
```

## API 接口

### 文件操作

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/files/list` | GET | 列出目录内容 |
| `/api/files/upload` | POST | 上传文件 |
| `/api/files/download` | GET | 下载文件 |
| `/api/files/delete` | POST | 删除文件/目录 |
| `/api/files/mkdir` | POST | 创建目录 |
| `/api/files/rename` | POST | 重命名 |

### 管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/users` | GET | 用户列表 |
| `/admin/users/create` | POST | 创建用户 |
| `/admin/permissions` | GET | 权限管理 |
| `/admin/permissions/grant` | POST | 授权 |
| `/admin/permissions/revoke` | POST | 撤销权限 |
| `/admin/logs` | GET | 审计日志 |

## 安全建议

1. ✅ 生产环境务必修改 `SECRET_KEY`
2. ✅ 使用强密码策略
3. ✅ 启用 HTTPS (Nginx 配置 SSL)
4. ✅ 定期备份数据库和文件
5. ✅ 限制上传文件类型和大小
6. ✅ 监控审计日志

## ❓ 常见问题

### Q: 上传失败怎么办？
A: 检查 `MAX_CONTENT_LENGTH` 配置和 Nginx 的 `client_max_body_size`。详见 [QUICKSTART.md](QUICKSTART.md)

### Q: 如何添加新用户？
A: 管理员登录后，进入"用户管理" → "新建用户"。详见 [QUICKSTART.md](QUICKSTART.md#第-4-步创建用户 1 分钟)

### Q: 如何配置目录权限？
A: 管理员进入"权限管理" → 选择用户 → 添加目录权限。详见 [QUICKSTART.md](QUICKSTART.md#第-5-步分配权限 1 分钟)

### Q: 支持哪些文件类型？
A: 默认支持所有文件类型上传。管理员可在 `config.py` 中配置白名单限制。

### Q: 支持中文文件名吗？
A: 支持，系统使用 UTF-8 编码，完美支持中文路径和文件名。

### Q: 忘记密码怎么办？
A: 管理员可在"用户管理"中重置密码。详见 [QUICKSTART.md](QUICKSTART.md#q-忘记密码怎么办)

### Q: 如何备份数据？
A: 备份 `file_manager.db` 和 `data/users/` 目录。详见 [QUICKSTART.md](QUICKSTART.md#q-如何备份数据)

## 🗺️ 开发路线图

> 📌 **当前状态**: ✅ v1.0.0 第一阶段已完成 (85-90%) - 内部使用稳定
> 
> 📅 **最新修复** (2026-03-15): 权限撤销、路径删除、路径格式标准化等 8 个 Bug
> 
> 详细更新历史请查看 [CHANGELOG.md](CHANGELOG.md)

### v1.1.0 (下一阶段)
- [ ] 批量文件操作（多选/批量上传/批量下载）
- [ ] 文件搜索功能
- [ ] 回收站功能（软删除）
- [ ] 文件历史版本

### v1.2.0
- [ ] 在线文件预览（图片/PDF/Office）
- [ ] 文件分享链接
- [ ] 外链密码保护
- [ ] 外链有效期设置

### v2.0.0 (长期规划)
- [ ] 多存储后端（S3/OSS/MinIO）
- [ ] 文件去重
- [ ] 传输加密
- [ ] 双因素认证 (2FA)
- [ ] API Rate Limiting

**想参与开发？查看 [CONTRIBUTING.md](CONTRIBUTING.md)**

## 📄 更新日志

查看完整的版本历史和更新记录：[CHANGELOG.md](CHANGELOG.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

- 🐛 报告问题：[GitHub Issues](https://github.com/your-repo/file_manager/issues)
- 💡 功能建议：[GitHub Discussions](https://github.com/your-repo/file_manager/discussions)
- 📝 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 支持

- 📖 完整文档：[INSTALL.md](INSTALL.md) | [QUICKSTART.md](QUICKSTART.md)
- 🚀 部署指南：[DEPLOY_LINUX.md](DEPLOY_LINUX.md)
- 📦 发布说明：[RELEASE_NOTES.md](RELEASE_NOTES.md)

---

**Made with ❤️ by NotJustSRE**
