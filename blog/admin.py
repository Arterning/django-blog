from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'is_published']
    list_filter = ['is_published', 'created_at', 'category']
    search_fields = ['title', 'content', 'tags']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
