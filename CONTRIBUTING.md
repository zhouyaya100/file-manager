# 贡献指南

感谢你对多用户文件管理系统的关注！欢迎贡献代码、报告问题或提出建议。

---

## 🤝 如何贡献

### 1. 报告问题 (Bug Report)

发现 Bug？请提交 Issue 并提供以下信息：

**问题描述模板:**
```markdown
### 问题描述
简要描述遇到的问题

### 复现步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

### 期望行为
应该发生什么

### 实际行为
实际发生了什么

### 环境信息
- 操作系统：Windows 11 / Ubuntu 22.04 / macOS 13
- Python 版本：3.11.0
- 浏览器：Chrome 120 / Firefox 121

### 截图/日志
如有错误截图或日志，请附上
```

### 2. 功能建议 (Feature Request)

有新功能想法？欢迎提交 Feature Request：

**功能建议模板:**
```markdown
### 功能描述
简要描述想要的功能

### 使用场景
为什么需要这个功能？解决什么问题？

### 实现建议
如果有实现思路，请描述

### 替代方案
是否考虑过其他解决方案？
```

### 3. 提交代码 (Code Contribution)

#### 3.1 Fork 项目

1. 点击 GitHub 页面右上角的 "Fork"
2. 克隆到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/file_manager.git
   cd file_manager
   ```

#### 3.2 创建分支

```bash
# 功能开发
git checkout -b feature/your-feature-name

# Bug 修复
git checkout -b fix/issue-123

# 文档更新
git checkout -b docs/update-readme
```

**分支命名规范:**
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关
- `chore/xxx` - 构建/工具相关

#### 3.3 开发代码

**代码规范:**
- 遵循 PEP 8 风格指南
- 使用 4 空格缩进
- 函数/类添加文档字符串
- 关键逻辑添加注释

**示例:**
```python
def upload_file(file, path):
    """
    上传文件到指定目录
    
    Args:
        file: FileStorage 对象
        path: 目标路径
        
    Returns:
        dict: {'success': True, 'filename': '...'} 或 {'success': False, 'error': '...'}
        
    Raises:
        PermissionError: 无访问权限
        ValueError: 文件类型不允许
    """
    # 检查权限
    if not check_permission(path, 'write'):
        raise PermissionError('无写入权限')
    
    # 检查文件类型
    if not allowed_file(file.filename):
        raise ValueError('不允许的文件类型')
    
    # ... 实现逻辑
```

#### 3.4 编写测试

为新增功能编写测试用例：

```python
def test_upload_file_success():
    """测试文件上传成功"""
    # 准备测试数据
    # 执行上传操作
    # 断言结果
    
def test_upload_file_no_permission():
    """测试无权限时上传失败"""
    # ...
```

#### 3.5 提交更改

```bash
# 添加文件
git add .

# 提交（使用规范的提交信息）
git commit -m "feat: 添加文件批量上传功能"

# 推送到远程
git push origin feature/your-feature-name
```

**提交信息规范:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型:**
- `feat` - 新功能
- `fix` - Bug 修复
- `docs` - 文档更新
- `style` - 代码格式（不影响功能）
- `refactor` - 重构
- `test` - 测试相关
- `chore` - 构建/工具相关

**示例:**
```
feat(upload): 添加文件批量上传功能

- 支持多选文件上传
- 显示上传进度
- 上传完成后显示结果统计

Closes #123
```

#### 3.6 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述
4. 等待代码审查

**PR 描述模板:**
```markdown
### 变更内容
简要描述本次 PR 的变更

### 相关 Issue
Closes #123

### 测试情况
- [x] 本地测试通过
- [x] 单元测试通过
- [ ] 集成测试通过

### 截图/演示
如有 UI 变更，请提供截图

### 其他说明
需要审查者特别注意的地方
```

---

## 📋 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/file_manager.git
cd file_manager
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装开发依赖（可选）

```bash
pip install pytest pytest-cov flake8 black
```

### 5. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_upload.py

# 查看测试覆盖率
pytest --cov=file_manager
```

### 6. 代码检查

```bash
# 代码风格检查
flake8 .

# 代码格式化
black .
```

---

## 🏗️ 项目结构

```
file_manager/
├── app.py                  # Flask 应用入口
├── config.py               # 配置文件
├── database.py             # 数据库模型
├── auth.py                 # 认证模块
├── permissions.py          # 权限模块
├── file_manager.py         # 文件操作模块
│
├── templates/              # HTML 模板
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── files.html
│   └── admin/
│       ├── users.html
│       ├── permissions.html
│       └── logs.html
│
├── static/                 # 静态资源
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       └── files.js
│
├── tests/                  # 测试代码（计划）
│   ├── test_auth.py
│   ├── test_permissions.py
│   └── test_files.py
│
└── docs/                   # 文档
    ├── README.md
    ├── INSTALL.md
    ├── QUICKSTART.md
    └── CONTRIBUTING.md
```

---

## 🎯 开发路线图

### v1.1.0 (进行中)

- [ ] 批量文件操作
- [ ] 文件搜索功能
- [ ] 回收站功能
- [ ] 文件历史版本

### v1.2.0 (规划中)

- [ ] 在线文件预览
- [ ] 文件分享链接
- [ ] 外链密码保护
- [ ] 外链有效期设置

### v2.0.0 (长期规划)

- [ ] 多存储后端（S3/OSS）
- [ ] 文件去重
- [ ] 双因素认证
- [ ] API Rate Limiting

**想参与某个功能开发？在 Issue 中留言认领！**

---

## 🔍 代码审查清单

提交 PR 前请自查：

### 代码质量
- [ ] 代码遵循 PEP 8 规范
- [ ] 无语法错误
- [ ] 无明显的性能问题
- [ ] 关键逻辑有注释

### 功能完整性
- [ ] 功能按预期工作
- [ ] 边界情况已处理
- [ ] 错误处理完善
- [ ] 输入验证完善

### 测试
- [ ] 新增测试用例
- [ ] 现有测试通过
- [ ] 测试覆盖率未下降

### 文档
- [ ] 更新 README（如有必要）
- [ ] 更新 API 文档（如有必要）
- [ ] 代码有文档字符串

### 安全
- [ ] 无 SQL 注入风险
- [ ] 无 XSS 风险
- [ ] 无路径遍历风险
- [ ] 敏感信息未硬编码

---

## 📞 联系方式

- **GitHub Issues**: 报告问题/功能建议
- **GitHub Discussions**: 讨论交流
- **Email**: your-email@example.com（如有）

---

## 📜 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

### 不可接受的行为

- ❌ 使用性化的语言或图像
- ❌ 人身攻击或侮辱性评论
- ❌ 公开或私下骚扰
- ❌ 未经许可发布他人信息
- ❌ 其他不道德或不专业的行为

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

通过贡献代码，你同意你的贡献遵循本项目的许可证。

---

## 🙏 致谢

感谢所有贡献者！

<a href="https://github.com/your-repo/file_manager/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=your-repo/file_manager" />
</a>

---

**开始贡献吧！** 🎉

第一次贡献？从 "good first issue" 标签的 Issue 开始！
