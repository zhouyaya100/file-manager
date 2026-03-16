# 贡献指南

感谢你考虑为 FileHub 项目做出贡献！🎉

## 📋 目录

- [代码规范](#代码规范)
- [提交 PR 流程](#提交 pr 流程)
- [Bug 报告](#bug-报告)
- [功能建议](#功能建议)
- [开发环境](#开发环境)

---

## 🛠️ 代码规范

### Python 代码风格

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# ✅ 好的写法
def get_user_permissions(user_id):
    """获取用户权限列表"""
    permissions = []
    return permissions

# ❌ 避免的写法
def getUserPermissions(userId):  # 驼峰命名
    permissions=[]  # 缺少空格
    return permissions
```

### 提交信息格式

```bash
<type>: <subject>

[optional body]
```

**Type 类型:**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具

**示例:**
```bash
git commit -m "feat: 添加批量用户导入功能"
git commit -m "fix: 修复邮箱唯一性约束冲突"
git commit -m "docs: 更新 README 安装步骤"
```

---

## 🚀 提交 PR 流程

### 1. Fork 项目

在 GitHub 页面点击右上角 **Fork** 按钮

### 2. 克隆到本地

```bash
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/file_manager.git
```

### 4. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 5. 开发并提交

```bash
# 修改代码...
git add .
git commit -m "feat: 添加 XXX 功能"
```

### 6. 同步上游更新

```bash
# 获取上游最新代码
git fetch upstream

# 合并到当前分支
git merge upstream/main

# 或变基（推荐）
git rebase upstream/main
```

### 7. 推送到远程

```bash
git push origin feature/your-feature-name
```

### 8. 创建 Pull Request

1. 访问你的 GitHub 仓库
2. 点击 **Compare & pull request**
3. 填写 PR 描述
4. 等待代码审查

---

## 🐛 Bug 报告

### 提交 Bug 前请确认

- [ ] 已搜索现有 Issues
- [ ] 使用最新版本
- [ ] 查阅过文档

### Bug 报告模板

```markdown
**问题描述**
简明扼要描述问题

**复现步骤**
1. 执行 '...'
2. 点击 '...'
3. 看到错误 '...'

**期望行为**
应该发生什么

**实际行为**
实际发生了什么

**环境信息**
- OS: Windows 11 / Ubuntu 22.04
- Python: 3.10.5
- 浏览器：Chrome 115

**截图**
如有必要，添加截图

**日志**
```
粘贴相关错误日志
```
```

---

## 💡 功能建议

### 功能建议模板

```markdown
**功能描述**
简明扼要描述建议的功能

**使用场景**
这个功能解决什么问题？

**实现建议**
如有想法，描述可能的实现方式

**替代方案**
是否考虑过其他解决方案？
```

---

## 💻 开发环境

### 本地开发设置

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\Activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如有

# 启动开发服务器
python start.py --debug
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 查看测试覆盖率
pytest --cov=file_manager
```

---

## 📝 文档贡献

### 文档更新

- 确保文档准确
- 使用清晰的中文
- 添加必要的示例
- 更新目录索引

### 代码注释

```python
def create_user(username, password, email=None):
    """
    创建新用户
    
    Args:
        username (str): 用户名
        password (str): 密码
        email (str, optional): 邮箱，为空时自动生成
    
    Returns:
        tuple: (user, error) - user 为用户对象，error 为错误信息
    
    Raises:
        IntegrityError: 当用户名或邮箱已存在时
    """
    pass
```

---

## 🔍 代码审查清单

提交 PR 前自查：

- [ ] 代码通过测试
- [ ] 遵循代码规范
- [ ] 添加必要的注释
- [ ] 更新相关文档
- [ ] 提交信息清晰
- [ ] 无敏感信息泄露
- [ ] 合并了上游最新代码

---

## 📧 联系方式

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/file_manager/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/YOUR_USERNAME/file_manager/discussions)

---

## 🙏 致谢

感谢所有为 FileHub 做出贡献的开发者！❤️

<a href="https://github.com/YOUR_USERNAME/file_manager/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=YOUR_USERNAME/file_manager" />
</a>

---

**Happy Coding! 🚀**
