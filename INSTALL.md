# 安装指南

多用户文件管理系统 v1.0.1 完整安装说明。

**最新版本**: v1.0.1 (2026-03-17)  
**主要更新**: 性能优化、CDN 修复、登录速度提升 70%

---

## 📋 目录

1. [系统要求](#系统要求)
2. [Windows 安装](#windows-安装)
3. [Linux 安装](#linux-安装)
4. [macOS 安装](#macos-安装)
5. [Docker 安装](#docker-安装)
6. [故障排查](#故障排查)

---

## 系统要求

### 最低配置
- **CPU**: 1 核心
- **内存**: 512MB
- **存储**: 1GB 可用空间
- **Python**: 3.8 或更高版本

### 推荐配置
- **CPU**: 2 核心+
- **内存**: 2GB+
- **存储**: 10GB+（根据文件存储需求）
- **Python**: 3.10+

### 支持的系统

| 操作系统 | 版本 | 状态 |
|----------|------|------|
| Windows | 10/11 | ✅ 支持 |
| Ubuntu | 20.04, 22.04 | ✅ 支持 |
| Debian | 10, 11, 12 | ✅ 支持 |
| CentOS | 7, 8, 9 | ✅ 支持 |
| macOS | 10.15+ | ✅ 支持 |

---

## Windows 安装

### 方法一：一键启动（推荐新手）

1. **下载项目文件**
   - 解压 `file_manager.zip` 到任意目录

2. **双击运行**
   ```
   双击 start.bat
   ```

3. **等待自动安装**
   - 自动创建虚拟环境
   - 自动安装依赖
   - 自动启动服务

4. **访问系统**
   - 浏览器打开：http://localhost:5000
   - 默认管理员：`admin` / `Admin@123`

### 方法二：手动安装

1. **安装 Python**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **验证安装**
   ```powershell
   python --version
   ```

3. **安装依赖**
   ```powershell
   cd file_manager
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```powershell
   python start.py
   ```

### 方法三：使用虚拟环境

1. **创建虚拟环境**
   ```powershell
   cd file_manager
   python -m venv venv
   ```

2. **激活虚拟环境**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **安装依赖**
   ```powershell
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```powershell
   python start.py
   ```

---

## Linux 安装

### Ubuntu/Debian

#### 1. 安装系统依赖

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

#### 2. 验证 Python 版本

```bash
python3 --version
# 应显示 Python 3.8.0 或更高
```

#### 3. 下载项目

```bash
# 方式 1: Git 克隆
git clone <your-repo-url>
cd file_manager

# 方式 2: 解压压缩包
unzip file_manager.zip
cd file_manager
```

#### 4. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 5. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 6. 启动服务

```bash
# 方式 1: 使用启动脚本
chmod +x start.sh
./start.sh

# 方式 2: 直接运行
python3 start.py
```

#### 7. 访问系统

浏览器打开：http://your-server-ip:5000

### CentOS/RHEL

#### 1. 安装系统依赖

```bash
# CentOS 8 / RHEL 8
sudo dnf install -y python3 python3-pip git

# CentOS 7
sudo yum install -y python3 python3-pip git
```

#### 2. 安装虚拟环境模块（如未包含）

```bash
sudo yum install -y python3-virtualenv
```

#### 3. 后续步骤

与 Ubuntu/Debian 相同（见上文步骤 3-7）

---

## macOS 安装

### 1. 安装 Homebrew（如未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. 安装 Python

```bash
brew install python@3.11
```

### 3. 验证安装

```bash
python3 --version
pip3 --version
```

### 4. 下载项目

```bash
# 解压或使用 Git
git clone <your-repo-url>
cd file_manager
```

### 5. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 6. 安装依赖

```bash
pip install -r requirements.txt
```

### 7. 启动服务

```bash
python3 start.py
```

---

## Docker 安装

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 方法一：使用 Dockerfile

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/users

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "start.py"]
```

构建并运行:

```bash
# 构建镜像
docker build -t file-manager .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --name file-manager \
  file-manager
```

### 方法二：使用 Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  file-manager:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - SECRET_KEY=your-secret-key-here
      - FLASK_ENV=production
    restart: unless-stopped
```

启动服务:

```bash
docker-compose up -d
```

查看日志:

```bash
docker-compose logs -f
```

停止服务:

```bash
docker-compose down
```

---

## 生产环境安装

### Ubuntu 生产部署（推荐）

详见：[DEPLOY_LINUX.md](DEPLOY_LINUX.md)

简要步骤:

1. 创建专用用户
2. 配置虚拟环境
3. 安装 Gunicorn
4. 配置 Nginx 反向代理
5. 配置 systemd 服务
6. 启用 HTTPS（Let's Encrypt）

### Windows 生产部署

使用 NSSM (Non-Sucking Service Manager):

1. 下载 NSSM: https://nssm.cc/download
2. 安装服务:
   ```cmd
   nssm install FileManager "C:\Python39\python.exe" "C:\file_manager\start.py"
   ```
3. 配置服务参数
4. 启动服务: `nssm start FileManager`

---

## 依赖包说明

### requirements.txt

```
Flask==2.3.3              # Web 框架
Werkzeug==2.3.7           # WSGI 工具
SQLAlchemy==2.0.20        # ORM
Flask-Login==0.6.2        # 用户会话管理
python-dotenv==1.0.0      # 环境变量
```

### 可选依赖（生产环境）

```
gunicorn==21.2.0          # WSGI HTTP 服务器
psycopg2-binary==2.9.7    # PostgreSQL 驱动
PyMySQL==1.1.0            # MySQL 驱动
python-magic==0.4.27      # 文件内容检查（可选）
python-clamd==1.0.2       # 病毒扫描（可选）
```

---

## 配置说明

### 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_KEY` | 生产必填 | 随机生成 | Flask 密钥 |
| `FLASK_ENV` | 可选 | development | 运行环境 |
| `DATABASE_URL` | 可选 | SQLite | 数据库连接 |
| `ALLOWED_EXTENSIONS` | 可选 | None | 允许的文件类型（逗号分隔） |

### 设置环境变量

**Linux/Mac:**
```bash
export SECRET_KEY='your-secret-key'
export FLASK_ENV='production'
```

**Windows (PowerShell):**
```powershell
$env:SECRET_KEY='your-secret-key'
$env:FLASK_ENV='production'
```

**Windows (CMD):**
```cmd
set SECRET_KEY=your-secret-key
set FLASK_ENV=production
```

---

## 验证安装

### 1. 检查服务状态

```bash
# 查看进程
ps aux | grep python

# 查看端口
netstat -tlnp | grep 5000
# 或
lsof -i :5000
```

### 2. 测试访问

```bash
curl http://localhost:5000
```

应返回 HTML 登录页面。

### 3. 检查日志

```bash
# 查看应用日志
tail -f file_manager/server.log

# 查看错误日志
tail -f file_manager/server.err.log
```

---

## 故障排查

### 问题 1: Python 版本过低

**错误**: `SyntaxError` 或 `ModuleNotFoundError`

**解决**:
```bash
# 检查版本
python --version

# 升级 Python
# Ubuntu
sudo apt install python3.11

# 使用 pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

### 问题 2: pip 安装失败

**错误**: `Could not find a version that satisfies the requirement`

**解决**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 3: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查找占用进程
lsof -i :5000
# 或
netstat -tlnp | grep 5000

# 终止进程
kill -9 <PID>

# 或修改端口
# 编辑 start.py，修改 port=5001
```

### 问题 4: 权限不足

**错误**: `Permission denied`

**解决**:
```bash
# Linux/Mac - 赋予执行权限
chmod +x start.sh

# 修复目录权限
sudo chown -R $USER:$USER file_manager

# 或使用 sudo（不推荐）
sudo ./start.sh
```

### 问题 5: 虚拟环境问题

**错误**: `command not found: python`

**解决**:
```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 6: 数据库锁定

**错误**: `database is locked`

**解决**:
```bash
# 停止服务
# 删除锁定文件
rm -f file_manager.db-shm
rm -f file_manager.db-wal

# 重启服务
python start.py
```

---

## 卸载

### 开发环境

```bash
# 删除虚拟环境
rm -rf venv

# 删除项目
rm -rf file_manager

# 删除全局安装的包（可选）
pip uninstall flask sqlalchemy flask-login
```

### 生产环境（Ubuntu）

```bash
# 停止服务
sudo systemctl stop file_manager
sudo systemctl disable file_manager

# 删除服务文件
sudo rm /etc/systemd/system/file_manager.service
sudo systemctl daemon-reload

# 删除应用目录
sudo rm -rf /opt/file_manager

# 删除日志
sudo rm -rf /var/log/file_manager

# 删除 Nginx 配置
sudo rm /etc/nginx/sites-available/file_manager
sudo rm /etc/nginx/sites-enabled/file_manager
sudo systemctl restart nginx
```

---

## 下一步

安装完成后：

1. 📖 阅读 [README.md](README.md) 了解功能
2. 🔐 登录并修改管理员密码
3. 👥 创建用户并分配权限
4. 📁 开始使用文件管理功能

---

**安装完成！如有问题请查看故障排查部分。** 🎉
