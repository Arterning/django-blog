from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    """博客文章模型"""
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    summary = models.TextField('摘要', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_published = models.BooleanField('已发布', default=True)

    # 可选的元数据字段（从frontmatter中读取）
    tags = models.CharField('标签', max_length=200, blank=True, help_text='多个标签用逗号分隔')
    category = models.CharField('分类', max_length=100, blank=True)

    class Meta:
        verbose_name = '博客文章'
        verbose_name_plural = '博客文章'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_summary(self):
        """如果没有摘要，从内容中提取前150个字符"""
        if self.summary:
            return self.summary
        return self.content[:150] + '...' if len(self.content) > 150 else self.content


class Comment(models.Model):
    """博客评论模型"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} 在 {self.post.title} 的评论'

    def is_reply(self):
        """判断是否为回复评论"""
        return self.parent is not None
