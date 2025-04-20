from django.db import models
from accounts.models import User


class SysAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    admin_id = models.CharField(max_length=100, primary_key=True)#工号
    name = models.CharField(max_length=100)#管理员姓名

# 学校的学下设学院
class College(models.Model):
    college_id = models.CharField(max_length=3,primary_key=True)
    college_name = models.CharField(max_length=15,unique=True)

    def __str__(self):
        return self.college_name

# 学院的下设专业
class Major(models.Model):
    major_id = models.CharField(max_length=2,primary_key=True)
    major_name = models.CharField(max_length=15,unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return self.major_name