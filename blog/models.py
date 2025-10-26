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
