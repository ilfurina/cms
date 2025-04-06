from django.db import models


class classes(models.Model):
    class_id = models.CharField(max_length=100, primary_key=True)
    join_code = models.IntegerField()
    class_name = models.CharField(max_length=100)
    class_size = models.IntegerField(default=1)
