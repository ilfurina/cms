import random

from django.db import models
from accounts.models import User
from student.models import Student


# 教师创建课程，学生可加入课程，教师可以在课程中发布实验、作业、考试等
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    teacher_id = models.CharField(max_length=100, primary_key=True) #教师工号
    name = models.CharField(max_length=100)  #用户姓名
    college = models.CharField(max_length=100,null=True, blank=True)#学院
    # user_type = models.CharField(max_length=10, default='teacher') #这字段没必要啊


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()#课程描述
    numbers = models.IntegerField(default=0)#班级人数，创建初始只有老师一人
    teacher = models.ForeignKey(
        'teacher.Teacher',
        on_delete=models.CASCADE,
        related_name='course'  # 允许通过teacher.courses反向查询
    )
    students = models.ManyToManyField(
        'student.Student',
        related_name='courses',  # 允许通过student.courses反向查询
        # through='Enrollment',
        blank=True  # 允许课程没有学生
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    title = models.CharField(max_length=100, default="课堂签到")
    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=10)  # 单位：分钟
    checkin_code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)

    def generate_code(self):
        # 生成4位数字验证码
        self.checkin_code = str(random.randint(1000, 9999))
        return self.checkin_code


