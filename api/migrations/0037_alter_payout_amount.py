# Generated by Django 5.0.2 on 2024-09-21 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_payout_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payout',
            name='amount',
            field=models.FloatField(default=0.05),
        ),
    ]
