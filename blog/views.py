from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Post
from .forms import MarkdownUploadForm
import os
import zipfile
import frontmatter
import markdown
import tempfile


# 用户认证视图
def register_view(request):
    """用户注册"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('post_list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})


def login_view(request):
    """用户登录"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                return redirect('post_list')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


def logout_view(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已成功登出。')
    return redirect('post_list')


# 博客列表和详情视图
def post_list(request):
    """博客列表页面（分页）"""
    posts = Post.objects.filter(is_published=True)
    paginator = Paginator(posts, 10)  # 每页显示10篇文章

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {'page_obj': page_obj})


def post_detail(request, pk):
    """博客详情页面"""
    post = get_object_or_404(Post, pk=pk, is_published=True)
    # 将markdown转换为HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    post.html_content = md.convert(post.content)
    return render(request, 'blog/post_detail.html', {'post': post})


def search_posts(request):
    """搜索博客文章"""
    query = request.GET.get('q', '').strip()

    if query:
        # 使用Q对象进行OR查询，搜索标题、内容、摘要、标签和分类
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__icontains=query) |
            Q(category__icontains=query),
            is_published=True
        ).distinct()
    else:
        posts = Post.objects.none()

    # 分页
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/search_results.html', {
        'page_obj': page_obj,
        'query': query,
        'total_results': posts.count()
    })


# 管理员功能
def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def upload_markdown(request):
    """管理员上传markdown文件"""
    if request.method == 'POST':
        form = MarkdownUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_type = request.POST.get('upload_type')

            if upload_type == 'single':
                # 单个文件上传
                md_file = request.FILES.get('single_file')
                process_markdown_file(md_file, request.user)
                messages.success(request, '文件上传成功！')

            elif upload_type == 'multiple':
                # 多个文件上传
                files = request.FILES.getlist('multiple_files')
                for md_file in files:
                    process_markdown_file(md_file, request.user)
                messages.success(request, f'成功上传 {len(files)} 个文件！')

            elif upload_type == 'zip':
                # ZIP压缩包上传
                zip_file = request.FILES.get('zip_file')
                count = process_zip_file(zip_file, request.user)
                messages.success(request, f'成功从压缩包中导入 {count} 个文件！')

            return redirect('upload_markdown')
    else:
        form = MarkdownUploadForm()

    return render(request, 'blog/upload_markdown.html', {'form': form})


def process_markdown_file(md_file, author):
    """处理单个markdown文件"""
    # 读取文件内容
    raw_content = md_file.read()

    # 尝试多种编码解码
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']
    content = None

    for encoding in encodings:
        try:
            content = raw_content.decode(encoding)
            break
        except (UnicodeDecodeError, AttributeError):
            continue

    # 如果所有编码都失败，使用errors='ignore'
    if content is None:
        content = raw_content.decode('utf-8', errors='ignore')

    # 移除NUL字符(0x00)，PostgreSQL不允许这些字符
    content = content.replace('\x00', '')

    # 尝试解析frontmatter
    try:
        post_data = frontmatter.loads(content)
        title = post_data.get('title', os.path.splitext(md_file.name)[0])
        tags = post_data.get('tags', '')
        category = post_data.get('category', '')
        summary = post_data.get('summary', '')
        content_body = post_data.content
    except:
        # 如果没有frontmatter，使用文件名作为标题
        title = os.path.splitext(md_file.name)[0]
        tags = ''
        category = ''
        summary = ''
        content_body = content

    # 如果tags是列表，转换为逗号分隔的字符串
    if isinstance(tags, list):
        tags = ', '.join(tags)

    # 清理所有字段，移除NUL字符
    title = str(title).replace('\x00', '')
    tags = str(tags).replace('\x00', '')
    category = str(category).replace('\x00', '')
    summary = str(summary).replace('\x00', '')
    content_body = str(content_body).replace('\x00', '')

    # 创建博客文章
    Post.objects.create(
        title=title,
        content=content_body,
        summary=summary,
        author=author,
        tags=tags,
        category=category
    )


def process_zip_file(zip_file, author):
    """处理ZIP压缩包中的所有markdown文件"""
    count = 0

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        for chunk in zip_file.chunks():
            temp_file.write(chunk)
        temp_path = temp_file.name

    # 解压并处理
    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.md') or file_name.endswith('.markdown'):
                with zip_ref.open(file_name) as md_file:
                    # 读取文件内容
                    raw_content = md_file.read()

                    # 尝试多种编码解码
                    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']
                    content = None

                    for encoding in encodings:
                        try:
                            content = raw_content.decode(encoding)
                            break
                        except (UnicodeDecodeError, AttributeError):
                            continue

                    # 如果所有编码都失败，使用errors='ignore'
                    if content is None:
                        content = raw_content.decode('utf-8', errors='ignore')

                    # 移除NUL字符(0x00)，PostgreSQL不允许这些字符
                    content = content.replace('\x00', '')

                    # 解析frontmatter
                    try:
                        post_data = frontmatter.loads(content)
                        title = post_data.get('title', os.path.splitext(os.path.basename(file_name))[0])
                        tags = post_data.get('tags', '')
                        category = post_data.get('category', '')
                        summary = post_data.get('summary', '')
                        content_body = post_data.content
                    except:
                        title = os.path.splitext(os.path.basename(file_name))[0]
                        tags = ''
                        category = ''
                        summary = ''
                        content_body = content

                    # 如果tags是列表，转换为逗号分隔的字符串
                    if isinstance(tags, list):
                        tags = ', '.join(tags)

                    # 清理所有字段，移除NUL字符
                    title = str(title).replace('\x00', '')
                    tags = str(tags).replace('\x00', '')
                    category = str(category).replace('\x00', '')
                    summary = str(summary).replace('\x00', '')
                    content_body = str(content_body).replace('\x00', '')

                    # 创建文章
                    Post.objects.create(
                        title=title,
                        content=content_body,
                        summary=summary,
                        author=author,
                        tags=tags,
                        category=category
                    )
                    count += 1

    # 删除临时文件
    os.remove(temp_path)

    return count
