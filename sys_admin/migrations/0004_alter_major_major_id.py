# Generated by Django 5.1.7 on 2025-04-22 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sys_admin', '0003_alter_college_college_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='major',
            name='major_id',
            field=models.CharField(max_length=5, primary_key=True, serialize=False),
        ),
    ]
