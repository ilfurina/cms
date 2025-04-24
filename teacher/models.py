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
class QuestionBase(models.Model):
    QUESTION_TYPES = [
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('fill', '填空题'),
        ('essay', '问答题')
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    content = models.TextField(verbose_name="题目内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class SingleChoiceQuestion(QuestionBase):
    options = models.JSONField(verbose_name="选项列表")  # 格式：["选项A", "选项B"...]
    correct_answer = models.CharField(max_length=10, verbose_name="正确答案")

class MultipleChoiceQuestion(QuestionBase):
    options = models.JSONField(verbose_name="选项列表")
    correct_answers = models.JSONField(verbose_name="正确答案集合")  # 格式：["A", "B"]

class FillInBlankQuestion(QuestionBase):
    correct_answer = models.TextField(verbose_name="参考答案")
    keywords = models.JSONField(null=True, verbose_name="关键词")  # 自动评分用

class EssayQuestion(QuestionBase):
    reference_answer = models.TextField(verbose_name="参考答案")
    scoring_rubric = models.JSONField(null=True, verbose_name="评分标准")


class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('homework', '作业'),
        ('exam', '考试')
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    questions = models.ManyToManyField(QuestionBase, through='AssignmentQuestion')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


    def status_badge(self):
        now = timezone.now()
        if now < self.start_time:
            return '<span class="badge bg-secondary">未开始</span>'
        elif self.start_time <= now <= self.end_time:
            return '<span class="badge bg-success">进行中</span>'
        else:
            return '<span class="badge bg-danger">已结束</span>'
    status_badge.allow_tags = True

    def student_count(self):
        return self.course.students.count()


class AssignmentQuestion(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionBase, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)



