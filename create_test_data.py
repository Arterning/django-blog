"""
创建测试数据脚本
用于快速测试博客功能
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Post

print("=" * 60)
print("Creating Test Data")
print("=" * 60)

# 1. 创建测试用户（如果不存在）
print("\n1. Checking for test user...")
username = 'testadmin'
password = 'test123456'

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': 'test@example.com',
        'is_staff': True,
        'is_superuser': True,
    }
)

if created:
    user.set_password(password)
    user.save()
    print(f"   [OK] Created test admin user:")
    print(f"       Username: {username}")
    print(f"       Password: {password}")
else:
    print(f"   [INFO] Test user '{username}' already exists")

# 2. 创建测试博客文章
print("\n2. Creating test blog posts...")

test_posts = [
    {
        'title': 'Django博客系统入门',
        'content': '''# Django博客系统入门

欢迎使用Django博客系统！这是一个功能完整的博客平台。

## 主要功能

1. **Markdown支持**：支持完整的Markdown语法
2. **标签分类**：可以为文章添加标签和分类
3. **深色模式**：支持深色/浅色主题切换

## 代码示例

```python
def hello_world():
    print("Hello, Django Blog!")
```

## 引用

> 这是一个引用示例

## 列表

- 项目1
- 项目2
- 项目3

祝使用愉快！
''',
        'summary': '这是一篇介绍Django博客系统的入门文章，包含了主要功能介绍和使用示例。',
        'tags': 'Django, Python, Web开发',
        'category': '教程',
    },
    {
        'title': 'Markdown语法快速参考',
        'content': '''# Markdown语法快速参考

这篇文章介绍常用的Markdown语法。

## 标题

使用 # 号表示标题，一个 # 是一级标题，两个 ## 是二级标题，以此类推。

## 强调

- **粗体文本**
- *斜体文本*
- ~~删除线~~

## 链接和图片

[这是一个链接](https://www.example.com)

## 代码

行内代码：`print("Hello")`

代码块：

```javascript
function hello() {
    console.log("Hello, World!");
}
```

## 表格

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

## 有序列表

1. 第一项
2. 第二项
3. 第三项
''',
        'summary': 'Markdown常用语法快速参考指南。',
        'tags': 'Markdown, 文档, 写作',
        'category': '参考',
    },
    {
        'title': 'Python最佳实践',
        'content': '''# Python最佳实践

分享一些Python开发的最佳实践。

## 1. 代码风格

遵循 PEP 8 代码风格指南：

```python
# 好的命名
def calculate_total_price(items):
    return sum(item.price for item in items)

# 使用列表推导式
squares = [x**2 for x in range(10)]
```

## 2. 异常处理

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
finally:
    cleanup()
```

## 3. 上下文管理器

```python
with open('file.txt', 'r') as f:
    content = f.read()
```

## 4. 类型注解

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## 总结

良好的编码习惯可以提高代码质量和可维护性。
''',
        'summary': 'Python开发最佳实践，包括代码风格、异常处理、上下文管理器等内容。',
        'tags': 'Python, 编程, 最佳实践',
        'category': '技术',
    },
]

created_count = 0
for post_data in test_posts:
    post, created = Post.objects.get_or_create(
        title=post_data['title'],
        defaults={
            'content': post_data['content'],
            'summary': post_data['summary'],
            'author': user,
            'tags': post_data['tags'],
            'category': post_data['category'],
        }
    )
    if created:
        created_count += 1
        print(f"   [OK] Created: {post.title}")
    else:
        print(f"   [INFO] Already exists: {post.title}")

print(f"\n   Total: {created_count} new posts created")

# 3. 显示统计信息
print("\n3. Database statistics:")
total_users = User.objects.count()
total_posts = Post.objects.count()
published_posts = Post.objects.filter(is_published=True).count()

print(f"   Users: {total_users}")
print(f"   Total posts: {total_posts}")
print(f"   Published posts: {published_posts}")

print("\n" + "=" * 60)
print("Test data created successfully!")
print("=" * 60)

if created:
    print(f"\nTest admin login:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")

print(f"\nYou can now:")
print(f"  1. Visit: http://127.0.0.1:8000/")
print(f"  2. Login with the test admin account")
print(f"  3. Upload your own markdown files")
