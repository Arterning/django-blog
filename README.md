# Django博客系统

一个基于Django + PostgreSQL + Tailwind CSS + jQuery构建的现代化博客系统。

## 功能特性

### 已实现功能

- ✅ 用户认证系统（注册、登录、登出）
- ✅ 管理员权限控制（只有管理员可以上传文章）
- ✅ Markdown文件导入
  - 单个文件上传
  - 多个文件批量上传
  - ZIP压缩包批量导入
  - 支持Frontmatter元数据解析
- ✅ 博客文章展示
  - 首页分页列表
  - 文章详情页面
  - Markdown渲染为HTML
- ✅ 深色/浅色模式切换
- ✅ 响应式设计（Tailwind CSS）

### 待实现功能

- ⏳ 评论系统
- ⏳ 点赞功能
- ⏳ 文章分类和标签筛选
- ⏳ 文章搜索功能
- ⏳ 用户个人主页

## 技术栈

- **后端**: Django 5.2.7
- **数据库**: PostgreSQL
- **前端**: Tailwind CSS + jQuery
- **Markdown处理**: python-frontmatter + markdown

## 安装和使用

### 1. 环境准备

确保已安装：
- Python 3.13+
- PostgreSQL
- uv (Python包管理器)

### 2. 克隆项目并安装依赖

```bash
cd django-blog
uv sync
```

### 3. 配置数据库

编辑 `mysite/settings.py`，修改数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. 运行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级管理员

```bash
python manage.py createsuperuser
```

### 6. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可查看博客首页。

## 使用指南

### 上传Markdown文件

1. 使用管理员账号登录
2. 点击导航栏的"上传文章"按钮
3. 选择上传方式：
   - **单个文件**：上传单个.md文件
   - **多个文件**：同时上传多个.md文件
   - **ZIP压缩包**：上传包含多个.md文件的压缩包

### Frontmatter格式

Markdown文件可以包含以下元数据：

```markdown
---
title: 文章标题
tags: [Python, Django, Web开发]
category: 技术
summary: 文章摘要
---

# 文章内容开始

正文内容...
```

如果没有frontmatter，系统将使用文件名作为标题。

## 项目结构

```
django-blog/
├── blog/                   # 博客应用
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   ├── forms.py           # 表单
│   ├── urls.py            # URL路由
│   ├── admin.py           # 管理后台
│   └── templates/         # 模板文件
│       └── blog/
│           ├── base.html
│           ├── post_list.html
│           ├── post_detail.html
│           ├── login.html
│           ├── register.html
│           └── upload_markdown.html
├── mysite/                # 项目配置
│   ├── settings.py        # 设置
│   ├── urls.py            # 主URL路由
│   └── wsgi.py
├── static/                # 静态文件
├── media/                 # 媒体文件
├── manage.py
└── README.md
```

## 主要功能说明

### 用户权限

- **普通用户**: 可以注册、登录、查看博客文章
- **管理员** (is_staff或is_superuser): 可以上传Markdown文件

### 深色模式

- 点击导航栏的主题切换按钮可在深色/浅色模式间切换
- 主题选择会保存在浏览器localStorage中

### Markdown渲染

系统使用markdown库将Markdown转换为HTML，支持：
- 标题、段落、列表
- 代码块和代码高亮
- 引用、表格
- 链接和图片

## 开发说明

### 添加新功能

1. 在 `blog/models.py` 中定义新的数据模型
2. 运行 `python manage.py makemigrations` 和 `python manage.py migrate`
3. 在 `blog/views.py` 中实现视图逻辑
4. 在 `blog/urls.py` 中添加URL路由
5. 创建相应的模板文件

### 自定义样式

项目使用Tailwind CSS，可以在模板中直接使用Tailwind类名。
如需添加自定义CSS，可在 `base.html` 的 `<style>` 标签中添加。

## 许可证

MIT License
