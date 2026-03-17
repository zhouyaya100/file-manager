# FileHub - 多用户文件管理系统 v1.0.1

🔐 基于 Flask 的企业级多用户文件管理系统，支持细粒度目录权限控制。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](CHANGELOG.md)

**在线文档:** [安装指南](INSTALL.md) | [快速上手](QUICKSTART.md) | [更新日志](CHANGELOG.md)

---

## ✨ 功能特性

### 核心功能
| 功能 | 描述 |
|------|------|
| 🔐 **多用户支持** | 独立账户，会话管理，角色权限 |
| 📁 **权限控制** | 按目录分配读/写权限，支持子目录继承 |
| 📊 **审计日志** | 记录所有关键操作，支持查询和筛选 |
| 🎨 **现代 UI** | 科技感设计，响应式布局，支持移动端 |

### 文件操作
- 📤 **上传下载** - 支持所有文件类型，最大 1GB
- 🗑️ **删除管理** - 文件/目录删除，操作可追溯
- ✏️ **重命名** - 文件和目录重命名
- 📂 **目录管理** - 创建多级目录，树形导航

### 管理功能
- 👥 **用户管理** - 创建/禁用/删除用户，密码重置
- 🔑 **权限管理** - 可视化权限配置，批量授权
- 📝 **日志审计** - 完整操作日志，支持导出

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

**通用启动 (推荐):**
```bash
python start.py
```

**自定义端口:**
```bash
python start.py --port 8080
```

**生产模式:**
```bash
python start.py --production
```

### 4. 访问系统

浏览器打开：**http://localhost:5000**

**默认管理员账户:**
```
用户名：admin
密码：Admin@123
```

⚠️ **首次登录后请立即修改密码！**

---

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
├── gunicorn.conf.py            # Gunicorn 生产配置
│
├── templates/                  # HTML 模板
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── files.html
│   ├── admin/
│   └── settings/
│
├── static/                     # 静态资源
│   ├── css/
│   ├── js/
│   └── images/
│
├── data/                       # 数据目录
│   └── users/                  # 用户文件存储
│
└── file_manager.db             # SQLite 数据库
```

---

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 会话密钥 | 开发模式自动生成 |
| `FLASK_ENV` | 运行环境 | `development` |
| `GUNICORN_BIND` | Gunicorn 绑定地址 | `0.0.0.0:5000` |
| `GUNICORN_WORKERS` | Gunicorn 工作进程数 | `CPU*2+1` |
| `LOG_DIR` | 日志目录 | `/var/log/file_manager` |

### 生产环境配置

1. **设置 SECRET_KEY:**
```bash
# Linux/Mac
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Windows PowerShell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

2. **使用 Gunicorn 启动:**
```bash
python start.py --production
```

3. **配置 Nginx 反向代理 (可选):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [📖 安装指南](INSTALL.md) | 详细安装步骤和依赖说明 |
| [🏃 快速上手](QUICKSTART.md) | 5 分钟快速开始教程 |
| [🐧 Linux 部署](DEPLOY_LINUX.md) | 生产环境部署完整指南 |
| [🔒 安全配置](SECURITY_CONFIG.md) | 安全加固和最佳实践 |
| [📦 发布说明](RELEASE_NOTES.md) | 版本更新日志 |
| [🤝 贡献指南](CONTRIBUTING.md) | 如何参与项目开发 |

---

## 🛠️ 开发指南

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\Activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python start.py --debug
```

### 数据库迁移

如需从 SQLite 迁移到 PostgreSQL/MySQL:

1. 安装驱动:
```bash
pip install psycopg2-binary  # PostgreSQL
# 或
pip install pymysql          # MySQL
```

2. 修改 `config.py`:
```python
DATABASE_URL = "postgresql://user:pass@localhost/dbname"
```

---

## 🤝 贡献代码

### GitHub 同步流程

#### 1. Fork 项目

在 GitHub 页面点击右上角 **Fork** 按钮

#### 2. 克隆到本地

```bash
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager
```

#### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/file_manager.git
```

#### 4. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

#### 5. 开发并提交

```bash
# 修改代码...
git add .
git commit -m "feat: 添加 XXX 功能"
```

#### 6. 同步上游更新

```bash
# 获取上游最新代码
git fetch upstream

# 合并到当前分支
git merge upstream/main

# 或变基
git rebase upstream/main
```

#### 7. 推送到远程

```bash
git push origin feature/your-feature-name
```

#### 8. 创建 Pull Request

在 GitHub 页面点击 **Compare & pull request**

---

### 提交信息规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构代码
test: 测试相关
chore: 构建/工具链相关
```

示例:
```bash
git commit -m "feat: 添加用户批量导入功能"
git commit -m "fix: 修复邮箱唯一性约束问题"
```

---

## 📋 常见问题

### Q: 上传文件失败？
A: 检查 `config.py` 中的 `MAX_CONTENT_LENGTH` 和 `UPLOAD_FOLDER` 权限

### Q: 无法创建用户？
A: 检查数据库是否有唯一性约束冲突，确保邮箱唯一

### Q: 生产环境性能优化？
A: 使用 Gunicorn + Nginx，调整 `GUNICORN_WORKERS` 参数

### Q: 如何备份数据？
A: 备份 `file_manager.db` 和 `data/users/` 目录

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下开源项目：
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

## 📧 联系方式

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/file_manager/issues)
- 📖 Wiki: [项目 Wiki](https://github.com/YOUR_USERNAME/file_manager/wiki)

---

**Made with ❤️ by FileHub Team**
