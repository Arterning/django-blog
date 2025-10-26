# 快速开始指南

## 📋 前置要求

在开始之前，请确保已安装：
- Python 3.13+
- PostgreSQL 数据库
- uv (Python包管理器)

## 🚀 快速启动步骤

### 1. 配置PostgreSQL数据库

**选项A：使用自动化脚本创建数据库（推荐）**

项目提供了自动创建数据库的脚本：

```bash
# 先配置.env文件（见步骤2），然后运行：
uv run python create_database.py
```

**选项B：手动创建数据库**

```bash
# 登录PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE django_blog;

# 退出
\q
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件（与manage.py同级），添加以下内容：

```env
# PostgreSQL数据库配置
DB_NAME=django_blog
DB_USER=postgres
DB_PASSWORD=你的数据库密码
DB_HOST=localhost
DB_PORT=5432
```

**重要提示**：
- ⚠️ 如果密码包含中文或特殊字符，建议修改为纯英文+数字
- ⚠️ 遇到编码问题请查看 [DATABASE_SETUP.md](DATABASE_SETUP.md) 详细配置指南

### 3. 运行数据库迁移

```bash
# 创建迁移文件（已经生成好了）
uv run python manage.py makemigrations

# 应用迁移到数据库
uv run python manage.py migrate
```

### 4. 创建超级管理员账号

```bash
uv run python manage.py createsuperuser
```

按提示输入：
- 用户名
- 邮箱（可选）
- 密码（输入两次）

### 5. 启动开发服务器

```bash
uv run python manage.py runserver
```

### 6. 访问网站

打开浏览器访问：
- **博客首页**: http://127.0.0.1:8000/
- **后台管理**: http://127.0.0.1:8000/admin/
- **登录页面**: http://127.0.0.1:8000/login/
- **注册页面**: http://127.0.0.1:8000/register/

## 📝 使用说明

### 上传博客文章

1. 使用超级管理员账号登录
2. 点击导航栏的"上传文章"按钮
3. 选择上传方式：
   - **单个文件**: 上传单个 .md 文件
   - **多个文件**: 同时选择多个 .md 文件上传
   - **ZIP压缩包**: 上传包含多个 .md 文件的压缩包

### Markdown文件格式

你的Markdown文件可以包含frontmatter元数据（可选）：

```markdown
---
title: 我的第一篇博客
tags: [Python, Django, Web开发]
category: 技术
summary: 这是一篇关于Django博客系统的介绍
---

# 文章标题

这里是文章内容...
```

如果不包含frontmatter，系统会自动使用文件名作为标题。

### 深色模式切换

点击导航栏右侧的月亮/太阳图标可以切换深色/浅色模式。

## 🛠️ 常用命令

```bash
# 启动服务器
uv run python manage.py runserver

# 创建迁移
uv run python manage.py makemigrations

# 应用迁移
uv run python manage.py migrate

# 创建超级用户
uv run python manage.py createsuperuser

# 进入Django Shell
uv run python manage.py shell

# 收集静态文件（生产环境）
uv run python manage.py collectstatic
```

## 🔧 常见问题

### 1. 数据库连接错误

确保：
- PostgreSQL服务正在运行
- 数据库名称、用户名、密码正确
- PostgreSQL监听在localhost:5432

### 2. 模块未找到错误

使用 `uv run` 前缀运行所有Python命令：
```bash
uv run python manage.py runserver
```

### 3. 上传文件时出错

确保：
- 已使用管理员账号登录（is_staff=True 或 is_superuser=True）
- 上传的是 .md 或 .markdown 格式文件
- ZIP文件中包含有效的Markdown文件

## 📚 下一步

- 查看 [README.md](README.md) 了解完整功能
- 访问 Django Admin 管理后台
- 尝试上传你的第一篇Markdown博客
- 自定义Tailwind CSS样式

## 🎯 功能预告

即将实现的功能：
- 评论系统
- 点赞功能
- 文章搜索
- 分类和标签筛选
- 用户个人主页

祝你使用愉快！
