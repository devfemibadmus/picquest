# Generated by Django 5.0.2 on 2024-09-08 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='earned',
            field=models.IntegerField(default=0),
        ),
    ]
