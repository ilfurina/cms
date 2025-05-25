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
    face_collected = models.BooleanField(default=False)

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey('teacher.Assignment', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submit_time = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0) # 存储学生作业总分
    is_submitted = models.BooleanField(default=False)
    # over = models.BooleanField(default=False) #记录是否被批改

class StudentAnswer(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
    question = models.ForeignKey('teacher.QuestionBase', on_delete=models.CASCADE)
    answer = models.JSONField()  # 存储不同题型的答案
    score = models.FloatField(default=0) # 存储每个题目的得分
