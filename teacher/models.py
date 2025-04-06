from django.db import models

class teacher(models.Model):
    uid = models.CharField(max_length=100, primary_key=True) #用户账号
    name = models.CharField(max_length=100)  #用户姓名
    password = models.CharField(max_length=100)