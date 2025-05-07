import random
from django.db import models
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from accounts.models import User
from student.models import Student
from sys_admin.models import Major,College
import os
from polymorphic.models import PolymorphicModel


# 教师创建课程，学生可加入课程，教师可以在课程中发布实验、作业、考试等
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    teacher_id = models.CharField(max_length=100, primary_key=True) #教师工号
    name = models.CharField(max_length=100)  #用户姓名
    college = models.ForeignKey(College, on_delete=models.CASCADE,null=True, blank=True)#学院



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
    major = models.ForeignKey(
        'sys_admin.Major',
        on_delete=models.CASCADE,
        related_name='courses',  # 允许通过major.courses反向查询
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


class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    file = models.FileField(upload_to='course_resources/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_extension(self):
        return self.filename.split('.')[-1] if '.' in self.filename else ''

# 习题库模型
from django.contrib.auth import get_user_model

User = get_user_model()
# 后续试一下注释掉此行直接使用模型中的User是否可行

class Question(models.Model):
    QUESTION_TYPES = (
        ('SC', '单选题'),
        ('MC', '多选题'),
        ('FB', '填空题'),
        ('QA', '问答题'),
    )

    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=QUESTION_TYPES)
    content = models.TextField(verbose_name="题目内容")

    # 用于选择题的选项（JSON存储）
    options = models.JSONField(null=True, blank=True)

    # 答案存储（根据题目类型不同格式不同）
    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "题目"
        verbose_name_plural = "题库"


class Exercise(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question, through='ExerciseQuestionRelation')
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "习题任务"
        verbose_name_plural = "习题集"

# 中间模型，用于记录将题库中的题目加入习题任务发布时的一些关联信息
class ExerciseQuestionRelation(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(default=10, verbose_name="题目分值")
    order = models.PositiveIntegerField(default=0, verbose_name="题目顺序")

    class Meta:
        ordering = ['order']

# 实验报告


