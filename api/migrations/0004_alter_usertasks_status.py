# Generated by Django 5.0.2 on 2024-09-08 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_earned_user_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertasks',
            name='status',
            field=models.CharField(choices=[('pendingTasks', 'pendingTasks'), ('passedTasks', 'passedTasks'), ('failedTasks', 'failedTasks')], default='pending', max_length=15),
        ),
    ]
