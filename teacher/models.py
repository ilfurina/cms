from django.db import models
from accounts.models import User
# 教师创建课程，学生可加入课程，教师可以在课程中发布实验、作业、考试等
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    teacher_id = models.CharField(max_length=100, primary_key=True) #教师工号
    name = models.CharField(max_length=100)  #用户姓名
    college = models.CharField(max_length=100,null=True, blank=True)#学院
    # user_type = models.CharField(max_length=10, default='teacher') #这字段没必要啊