from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('profile/', views.user_profile, name='profile'),  # 添加个人主页路由
]