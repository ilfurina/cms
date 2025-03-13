from django.db import models

from classes.models import Class
from users.models import User


class Experiment(models.Model):
    title = models.CharField(max_length=200)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateTimeField()

class Submission(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.FileField(upload_to='reports/')
    video = models.FileField(upload_to='videos/', null=True)
    score = models.IntegerField(null=True)