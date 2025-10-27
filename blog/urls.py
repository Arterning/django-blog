from django.urls import path
from . import views

urlpatterns = [
    # 认证相关
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 博客相关
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('search/', views.search_posts, name='search_posts'),

    # 管理员功能
    path('upload/', views.upload_markdown, name='upload_markdown'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),

    # 评论功能
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
