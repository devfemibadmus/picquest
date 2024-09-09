from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    balance = models.IntegerField(default=0)
    daily_task = models.IntegerField(default=3)
    is_verify = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password'] 
    
    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class Documents(models.Model):
    theFile = models.FileField(upload_to='Documents/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.theFile.url}"

class Tasks(models.Model):
    title = models.CharField(max_length=50)
    amount = models.FloatField()
    description = models.CharField(max_length=200)

    @property
    def amounts(self):
        return f"${self.amount}"

    def __str__(self):
        return f"{self.title}"

class UserTasks(models.Model):
    STATUS_CHOICES = [
        ('pendingTasks', 'pendingTasks'),
        ('passedTasks', 'passedTasks'),
        ('failedTasks', 'failedTasks'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos/")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendingTasks')

    def __str__(self):
        return f"{self.task.title}"

class Token(models.Model):
    key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_string(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.key}"

class History(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

