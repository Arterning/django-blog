from django import forms


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
