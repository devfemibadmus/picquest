from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pendTasks = models.IntegerField(default=0)
    failTasks = models.IntegerField(default=0)
    passTasks = models.IntegerField(default=0)
    email = models.EmailField(unique=True)
    balance = models.IntegerField(default=0)
    daily_task = models.IntegerField(default=3)
    is_verify = models.BooleanField(default=False)
    hasPaid = models.BooleanField(default=False)
    documentSubmitted = models.BooleanField(default=False)
    referral = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referred_users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password'] 
    
    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class Document(models.Model):
    govID = models.FileField(upload_to='Documents/Gov/')
    stuID = models.FileField(upload_to='Documents/Student/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name

class Task(models.Model):
    title = models.CharField(max_length=50)
    amount = models.FloatField()
    description = models.CharField(max_length=200)

    @property
    def amounts(self):
        return f"${self.amount}"

    def __str__(self):
        return f"{self.title} {self.amount}"

class UserTask(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="User Tasks/")

    def __str__(self):
        return self.task.title

class Token(models.Model):
    key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_string(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key

class PayOut(models.Model):
    ACTION_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('pending debit', 'Pending Debit'),
        ('pending credit', 'Pending Credit'),
    ]
    
    DESCRIPTION_CHOICES = [
        ('Funds have been successfully withdrawn from your account as per your request for cash out or transfer.', 'Funds have been successfully withdrawn from your account as per your request for cash out or transfer.'),
        ('Earned money has been credited to your account from completed tasks or job payments.', 'Earned money has been credited to your account from completed tasks or job payments.'),
        ('Your request to withdraw funds is currently under review and is awaiting approval for processing.', 'Your request to withdraw funds is currently under review and is awaiting approval for processing.'),
        ('Credit for the tasks you’ve completed is pending and will be added to your account once reviewed.', 'Credit for the tasks you’ve completed is pending and will be added to your account once reviewed.'),
        ('Credit for Referral will be added to your account once the referred user verifies their account.', 'Credit for Referral will be added to your account once the referred user verifies their account.'),
    ]
    
    amount = models.CharField(max_length=50)
    dates = models.DateField(default=timezone.now)
    action = models.CharField(max_length=15, choices=ACTION_CHOICES, default='pending debit')
    description = models.CharField(max_length=200, choices=DESCRIPTION_CHOICES, default='Your request to withdraw funds is currently under review and is awaiting approval for processing.')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.action == 'debit':
            self.description = 'Funds have been successfully withdrawn from your account as per your request for cash out or transfer.'
        elif self.action == 'credit':
            self.description = 'Earned money has been credited to your account from completed tasks or job payments.'
        elif self.action == 'pending debit':
            self.description = 'Your request to withdraw funds is currently under review and is awaiting approval for processing.'
        elif self.action == 'pending credit':
            self.description = 'Credit for the tasks you’ve completed is pending and will be added to your account once reviewed.'
        elif self.action == 'referral':
            self.action = 'pending credit'
            self.description = 'Credit for Referral will be added to your account once the referred user verifies their account.'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.amount

class VerificationFee(models.Model):
    name = models.CharField(max_length=225)
    reference = models.CharField(max_length=225, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


