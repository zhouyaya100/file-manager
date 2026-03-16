# 快速参考卡片 📋

## 🚀 启动命令

```bash
# 开发模式
python start.py

# 自定义端口
python start.py --port 8080

# 生产模式
python start.py --production

# 调试模式
python start.py --debug
```

---

## 🔧 Git 常用命令

```bash
# 初始化
git init
git add .
git commit -m "initial commit"

# 关联 GitHub
git remote add origin https://github.com/USER/file_manager.git
git push -u origin main

# 日常同步
git status
git add .
git commit -m "feat: xxx"
git push

# 拉取更新
git pull origin main

# 查看历史
git log --oneline -5
```

---

## 📦 依赖管理

```bash
# 安装依赖
pip install -r requirements.txt

# 导出依赖
pip freeze > requirements.txt

# 更新依赖
pip install --upgrade -r requirements.txt
```

---

## 🗄️ 数据库操作

```bash
# 备份数据库
cp file_manager.db file_manager.db.backup

# 查看 SQLite 内容
sqlite3 file_manager.db ".tables"
sqlite3 file_manager.db "SELECT * FROM users;"
```

---

## 🔐 默认账户

```
用户名：admin
密码：Admin@123
```

⚠️ **首次登录后立即修改密码！**

---

## 📁 关键目录

```
file_manager/
├── data/users/      # 用户上传文件
├── templates/       # HTML 模板
├── static/          # CSS/JS/图片
└── file_manager.db  # 数据库
```

---

## ⚙️ 环境变量

```bash
# Flask 密钥
export SECRET_KEY="your-secret-key"

# 生产环境
export FLASK_ENV=production

# Gunicorn 配置
export GUNICORN_WORKERS=4
export GUNICORN_BIND="0.0.0.0:5000"
```

---

## 🐛 故障排查

```bash
# 查看进程
ps aux | grep python
ps aux | grep gunicorn

# 查看端口
netstat -tlnp | grep 5000

# 查看日志
tail -f audit.log
```

---

## 📊 系统要求

- Python 3.8+
- 2GB+ RAM
- 10GB+ 存储

---

## 🔗 重要文档

- [README.md](README.md) - 项目说明
- [INSTALL.md](INSTALL.md) - 安装指南
- [QUICKSTART.md](QUICKSTART.md) - 快速上手
- [GITHUB_SYNC.md](GITHUB_SYNC.md) - GitHub 同步
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

---

**打印此卡片贴在桌边！📌**
