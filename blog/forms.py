from django import forms
from .models import Post, Comment


class MultipleFileInput(forms.ClearableFileInput):
    """支持多文件上传的Widget"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """支持多文件上传的Field"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MarkdownUploadForm(forms.Form):
    """Markdown文件上传表单"""
    single_file = forms.FileField(
        required=False,
        label='单个文件',
        widget=forms.FileInput(attrs={'accept': '.md,.markdown'})
    )
    multiple_files = MultipleFileField(
        required=False,
        label='多个文件',
        widget=MultipleFileInput(attrs={'accept': '.md,.markdown'})
    )
    zip_file = forms.FileField(
        required=False,
        label='ZIP压缩包',
        widget=forms.FileInput(attrs={'accept': '.zip'})
    )


class PostForm(forms.ModelForm):
    """博客文章创建/编辑表单"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'summary', 'tags', 'category', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': '请输入文章标题'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': '支持Markdown格式',
                'rows': 15
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': '文章摘要(可选,留空将自动从内容提取)',
                'rows': 3
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': '多个标签用逗号分隔,如: Python, Django, Web开发'
            }),
            'category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white',
                'placeholder': '文章分类,如: 技术教程'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            })
        }
        labels = {
            'title': '文章标题',
            'content': '文章内容',
            'summary': '文章摘要',
            'tags': '标签',
            'category': '分类',
            'is_published': '立即发布'
        }


class CommentForm(forms.ModelForm):
    """评论表单"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-none',
                'placeholder': '发表你的评论... 支持Markdown语法和Emoji表情 😊',
                'rows': 4,
                'id': 'comment-textarea'
            })
        }
        labels = {
            'content': ''
        }
