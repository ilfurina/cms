from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


# 用户模型
class User(AbstractUser):
    objects = UserManager()
    USER_TYPE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    # 用邮箱作为登录标识（需自定义认证后端）
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # 命令行创建超级用户时需要的字段

    def __str__(self):
        return self.email

class CaptchaModel(models.Model):
    email = models.EmailField(unique=True)
    captcha = models.CharField(max_length=4)
    create_time = models.DateTimeField(auto_now_add=True)

