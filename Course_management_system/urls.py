from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    # 其他 URL 配置
]