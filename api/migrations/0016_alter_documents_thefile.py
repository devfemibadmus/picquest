# Generated by Django 5.0.2 on 2024-09-17 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_documents_is_downloaded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='theFile',
            field=models.FileField(null=True, upload_to='Documents/'),
        ),
    ]
