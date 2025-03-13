from django.db import models

from users.models import User


class Class(models.Model):
    ClassID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_classes')
    students = models.ManyToManyField(User, related_name='joined_classes')
    code = models.CharField(max_length=10, unique=True)  # 班级加入码

