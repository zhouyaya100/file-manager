# Linux 部署指南

快速在 Linux 服务器上部署文件管理系统。

## 系统要求

- Ubuntu 20.04+ / Debian 10+ / CentOS 7+
- Python 3.8+
- 2GB+ RAM
- 10GB+ 存储空间

---

## 快速部署（5 分钟）

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx git

# CentOS/RHEL
sudo yum install -y python3 python3-pip python3-devel nginx git
```

### 2. 克隆/上传项目

```bash
# 方式 1: Git 克隆
git clone <your-repo-url>
cd file_manager

# 方式 2: 上传压缩包后解压
unzip file_manager.zip
cd file_manager
```

### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 测试运行

```bash
# 赋予执行权限
chmod +x start.sh

# 启动服务
./start.sh
```

访问 http://your-server-ip:5000 测试

---

## 生产环境部署（推荐）

### 1. 创建专用用户

```bash
sudo useradd -r -s /bin/false filemanager
```

### 2. 配置应用目录

```bash
# 复制项目到/opt
sudo cp -r file_manager /opt/file_manager
sudo chown -R filemanager:filemanager /opt/file_manager

# 创建日志目录
sudo mkdir -p /var/log/file_manager
sudo chown filemanager:filemanager /var/log/file_manager

# 创建 PID 目录
sudo mkdir -p /var/run/file_manager
sudo chown filemanager:filemanager /var/run/file_manager
```

### 3. 配置环境变量

```bash
# 创建环境文件
sudo nano /opt/file_manager/.env

# 添加以下内容：
SECRET_KEY=your-secure-random-key-here
FLASK_ENV=production
```

生成安全密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 配置 Gunicorn

编辑 `gunicorn.conf.py`，修改：
```python
chdir = "/opt/file_manager"
accesslog = "/var/log/file_manager/access.log"
errorlog = "/var/log/file_manager/error.log"
```

### 5. 创建 Systemd 服务

```bash
# 复制服务文件
sudo cp file_manager.service /etc/systemd/system/

# 编辑服务文件（修改路径）
sudo nano /etc/systemd/system/file_manager.service
```

确保修改：
- `WorkingDirectory=/opt/file_manager`
- `ExecStart=/opt/file_manager/venv/bin/gunicorn ...`
- `Environment="SECRET_KEY=..."`

### 6. 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable file_manager
sudo systemctl start file_manager

# 检查状态
sudo systemctl status file_manager
```

### 7. 配置 Nginx

```bash
# 复制配置
sudo cp nginx.conf.example /etc/nginx/sites-available/file_manager

# 编辑配置（修改域名和路径）
sudo nano /etc/nginx/sites-available/file_manager

# 启用站点
sudo ln -s /etc/nginx/sites-available/file_manager /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 8. 配置防火墙

```bash
# Ubuntu (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## HTTPS 配置（推荐）

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu
sudo yum install certbot python3-certbot-nginx  # CentOS

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期（已自动配置 cron）
sudo certbot renew --dry-run
```

---

## 数据库迁移

如果从 SQLite 迁移到 PostgreSQL/MySQL：

```bash
# 安装驱动
pip install psycopg2-binary  # PostgreSQL
pip install pymysql          # MySQL

# 修改 config.py
DATABASE_URL = "postgresql://user:pass@localhost/dbname"
# 或
DATABASE_URL = "mysql+pymysql://user:pass@localhost/dbname"
```

---

## 常用命令

```bash
# 查看服务状态
sudo systemctl status file_manager

# 重启服务
sudo systemctl restart file_manager

# 查看日志
sudo journalctl -u file_manager -f
sudo tail -f /var/log/file_manager/access.log

# 进入虚拟环境
cd /opt/file_manager
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt --upgrade

# 备份数据库
cp /opt/file_manager/file_manager.db /backup/file_manager_$(date +%Y%m%d).db
```

---

## 故障排查

### 服务无法启动

```bash
# 查看详细错误
sudo journalctl -u file_manager --no-pager -n 50

# 检查端口占用
sudo lsof -i :5000

# 检查权限
ls -la /opt/file_manager
ls -la /var/log/file_manager
```

### Nginx 502 Bad Gateway

```bash
# 检查 Gunicorn 是否运行
sudo systemctl status file_manager

# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/file_manager_error.log
```

### 权限问题

```bash
# 修复权限
sudo chown -R filemanager:filemanager /opt/file_manager
sudo chmod -R 755 /opt/file_manager
```

---

## 性能优化

### 调整 Gunicorn 工作进程

根据服务器配置调整 `gunicorn.conf.py`：
```python
workers = 4  # 小服务器：2-4，大服务器：8-16
threads = 2  # I/O 密集型可增加
```

### 启用缓存

在 Nginx 中配置静态文件缓存：
```nginx
location /static {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 数据库优化

对于大量用户/文件：
- 迁移到 PostgreSQL
- 添加数据库索引
- 定期清理审计日志

---

## 安全加固

1. ✅ 修改默认管理员密码
2. ✅ 配置防火墙仅开放必要端口
3. ✅ 启用 HTTPS
4. ✅ 定期备份数据库
5. ✅ 监控系统资源使用
6. ✅ 更新系统和依赖包

```bash
# 定期更新
sudo apt update && sudo apt upgrade -y
pip list --outdated  # 检查 Python 包更新
```

---

## 备份策略

```bash
#!/bin/bash
# backup.sh - 每日备份脚本

BACKUP_DIR="/backup/file_manager"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/file_manager/file_manager.db $BACKUP_DIR/file_manager_$DATE.db

# 备份用户文件
tar -czf $BACKUP_DIR/users_$DATE.tar.gz /opt/file_manager/data/users

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

添加到 crontab：
```bash
0 2 * * * /opt/file_manager/backup.sh
```

---

部署完成后，访问 http://your-domain.com 登录使用！
