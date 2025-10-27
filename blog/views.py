from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Post, Comment
from .forms import MarkdownUploadForm, PostForm, CommentForm
import os
import zipfile
import frontmatter
import markdown
import tempfile
import re


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

    # 获取评论（只获取顶级评论，回复通过parent关系获取）
    comments = post.comments.filter(parent=None).select_related('author').prefetch_related('replies__author')

    # 处理评论提交
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # 处理回复（如果有parent_id）
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment.parent = parent_comment

            comment.save()
            messages.success(request, '评论发表成功！')
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()

    # 转换评论内容为HTML（支持Markdown）
    for comment in comments:
        comment.html_content = md.convert(comment.content)
        for reply in comment.replies.all():
            reply.html_content = md.convert(reply.content)

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form,
        'comment_count': post.comments.count()
    })


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


@login_required
@user_passes_test(is_admin)
def create_post(request):
    """管理员创建新博客文章"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '博客文章创建成功！')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {
        'form': form,
        'title': '创建新文章',
        'button_text': '发布文章'
    })


@login_required
@user_passes_test(is_admin)
def edit_post(request, pk):
    """管理员编辑博客文章"""
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '博客文章更新成功！')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'title': '编辑文章',
        'button_text': '保存修改'
    })


@login_required
@user_passes_test(is_admin)
def delete_post(request, pk):
    """管理员删除博客文章"""
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, '博客文章已删除！')
        return redirect('post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def delete_comment(request, pk):
    """删除评论（评论作者或管理员可删除）"""
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk

    # 检查权限：评论作者或管理员可以删除
    if request.user == comment.author or request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            comment.delete()
            messages.success(request, '评论已删除！')
            return redirect('post_detail', pk=post_pk)
    else:
        messages.error(request, '你没有权限删除此评论！')
        return redirect('post_detail', pk=post_pk)

    return redirect('post_detail', pk=post_pk)


def clean_notion_filename(filename):
    """
    清理Notion导出的文件名，去掉UUID哈希
    例如: "2025 211130a0ce0b80e8a540fd3052af5f90.md" -> "2025.md"
    """
    # 去掉文件扩展名
    name_without_ext = os.path.splitext(filename)[0]

    # Notion UUID 格式: 32个十六进制字符
    # 匹配模式: 文件名后面跟着空格和32位十六进制字符
    pattern = r'\s+[0-9a-f]{32}$'
    cleaned_name = re.sub(pattern, '', name_without_ext, flags=re.IGNORECASE)

    # 如果没有匹配到Notion格式，返回原始文件名（不含扩展名）
    return cleaned_name if cleaned_name else name_without_ext


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

    # 清理文件名（去掉Notion UUID）
    cleaned_filename = clean_notion_filename(md_file.name)

    # 尝试解析frontmatter
    try:
        post_data = frontmatter.loads(content)
        title = post_data.get('title', cleaned_filename)
        tags = post_data.get('tags', '')
        category = post_data.get('category', '')
        summary = post_data.get('summary', '')
        content_body = post_data.content
    except:
        # 如果没有frontmatter，使用清理后的文件名作为标题
        title = cleaned_filename
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

                    # 清理文件名（去掉Notion UUID）
                    cleaned_filename = clean_notion_filename(os.path.basename(file_name))

                    # 解析frontmatter
                    try:
                        post_data = frontmatter.loads(content)
                        title = post_data.get('title', cleaned_filename)
                        tags = post_data.get('tags', '')
                        category = post_data.get('category', '')
                        summary = post_data.get('summary', '')
                        content_body = post_data.content
                    except:
                        # 如果没有frontmatter，使用清理后的文件名作为标题
                        title = cleaned_filename
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
