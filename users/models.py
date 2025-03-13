from django.db import models
# users/models.py
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(models.Model):
    UserID = models.IntegerField(primary_key=True)
    identity = models.CharField(max_length=20) # 用户身份
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    #密码加密存储
    password = models.CharField(max_length=128)

# classes/models.py


# experiments/models.py



