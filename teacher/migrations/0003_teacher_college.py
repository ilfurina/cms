# Generated by Django 5.1.7 on 2025-04-20 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sys_admin', '0003_alter_college_college_id'),
        ('teacher', '0002_remove_teacher_college'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='college',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sys_admin.college'),
        ),
    ]
