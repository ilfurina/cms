from django.db import models
from accounts.models import User
from sys_admin.models import College,Major

# 学生属于某个班级，可以加入老师创建的课程
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    student_id = models.CharField(max_length=100, primary_key=True)#学号
    name = models.CharField(max_length=100)#姓名
    college = models.ForeignKey(College, on_delete=models.CASCADE,null=True, blank=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE,null=True, blank=True)

