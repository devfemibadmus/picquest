# Generated by Django 5.0.2 on 2024-09-21 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_payout_completed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payout',
            old_name='completed',
            new_name='checkout',
        ),
        migrations.AlterField(
            model_name='payout',
            name='description',
            field=models.CharField(choices=[('Funds have been successfully withdrawn from your account as per your request for cash out or transfer.', 'Funds have been successfully withdrawn from your account as per your request for cash out or transfer.'), ('Earned money has been credited to your account from completed tasks or job payments.', 'Earned money has been credited to your account from completed tasks or job payments.'), ('Referral Earned money has been credited to your account from completed tasks or job payments.', 'Referral Earned money has been credited to your account from completed tasks or job payments.'), ('Your request to withdraw funds is currently under review and is awaiting approval for processing.', 'Your request to withdraw funds is currently under review and is awaiting approval for processing.'), ('Credit for the tasks you’ve completed is pending and will be added to your account once reviewed.', 'Credit for the tasks you’ve completed is pending and will be added to your account once reviewed.'), ('Credit for Referral will be added to your account once the referred user verifies their account.', 'Credit for Referral will be added to your account once the referred user verifies their account.')], default='Your request to withdraw funds is currently under review and is awaiting approval for processing.', max_length=200),
        ),
    ]
