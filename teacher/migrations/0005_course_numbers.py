# Generated by Django 5.1.7 on 2025-04-10 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0004_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='numbers',
            field=models.IntegerField(default=1),
        ),
    ]
