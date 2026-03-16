# GitHub 同步指南 🚀

快速将项目上传到 GitHub 并同步更新。

---

## 📦 首次上传到 GitHub

### 1. 在 GitHub 创建空仓库

访问 https://github.com/new

- **Repository name**: `file_manager` (或你想要的名字)
- **Description**: 多用户文件管理系统
- **Visibility**: Public (公开) 或 Private (私有)
- ❌ **不要** 勾选 "Add README"
- ❌ **不要** 勾选 ".gitignore"
- ❌ **不要** 勾选 "Choose a license"

点击 **Create repository**

### 2. 本地初始化 Git

```bash
cd file_manager

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "initial commit: FileHub v1.0.0"
```

### 3. 关联 GitHub 仓库

```bash
# 添加远程仓库 (替换 YOUR_USERNAME 为你的 GitHub 用户名)
git remote add origin https://github.com/YOUR_USERNAME/file_manager.git

# 推送到 GitHub
git push -u origin main
```

✅ 完成！刷新 GitHub 页面查看代码。

---

## 🔄 日常同步流程

### 提交本地修改

```bash
# 1. 查看改动
git status

# 2. 添加文件
git add .
# 或添加特定文件
git add README.md config.py

# 3. 提交
git commit -m "feat: 添加 XXX 功能"
# 或
git commit -m "fix: 修复 XXX 问题"

# 4. 推送到 GitHub
git push
```

### 从 GitHub 拉取更新

```bash
# 拉取远程最新代码
git pull origin main

# 如果有冲突，解决后再次提交
```

---

## 🌿 分支管理

### 创建功能分支

```bash
# 基于 main 创建新分支
git checkout -b feature/new-feature

# 开发...

# 提交并推送
git add .
git commit -m "feat: 完成新功能"
git push origin feature/new-feature
```

### 合并到主分支

1. 在 GitHub 创建 Pull Request
2. 等待代码审查
3. 合并后删除分支

或在本地合并：
```bash
git checkout main
git merge feature/new-feature
git push origin main
```

---

## 🔧 常见问题

### Q: 推送失败 "remote origin already exists"

```bash
# 删除现有 remote
git remote remove origin

# 重新添加
git remote add origin https://github.com/YOUR_USERNAME/file_manager.git
```

### Q: 推送被拒绝 (rejected)

```bash
# 拉取远程代码并合并
git pull --rebase origin main

# 解决冲突后
git add <files>
git rebase --continue

# 再次推送
git push
```

### Q: 误提交了敏感信息

```bash
# 撤销最后一次提交 (保留改动)
git reset --soft HEAD~1

# 修改 .gitignore 排除敏感文件
# 然后重新提交
git add .
git commit -m "正确的提交信息"
```

### Q: 查看提交历史

```bash
# 简洁视图
git log --oneline

# 图形视图
git log --graph --oneline --all
```

---

## 📝 提交信息规范

使用语义化提交：

```bash
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 工具/构建
```

示例：
```bash
git commit -m "feat: 添加批量用户导入功能"
git commit -m "fix: 修复邮箱唯一性约束问题"
git commit -m "docs: 更新 README 安装步骤"
```

---

## 🔐 SSH 方式推送 (可选)

使用 SSH 避免每次输入密码：

### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

### 2. 添加公钥到 GitHub

```bash
# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制内容，访问：
# https://github.com/settings/keys
# 点击 "New SSH key" 粘贴
```

### 3. 切换到 SSH 方式

```bash
# 修改 remote URL
git remote set-url origin git@github.com:YOUR_USERNAME/file_manager.git

# 验证
git remote -v
```

---

## 📊 查看仓库状态

```bash
# 查看远程仓库
git remote -v

# 查看分支
git branch -a

# 查看状态
git status

# 查看最近提交
git log --oneline -5
```

---

## 🎯 最佳实践

1. **频繁提交** - 小步快跑，每次提交一个功能点
2. **清晰信息** - 提交信息说明做了什么，为什么
3. **及时同步** - 定期 pull 远程代码，避免大冲突
4. **分支开发** - 新功能在分支开发，完成后再合并
5. **代码审查** - 重要改动通过 PR 审查

---

## 📚 更多资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 入门](https://docs.github.com/en/get-started)
- [语义化提交规范](https://www.conventionalcommits.org/)

---

**Happy Coding! 🚀**
