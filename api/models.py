from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    balance = models.IntegerField(default=0)
    is_verify = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}"

class Documents(models.Model):
    theFile = models.FileField(upload_to='Documents/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.theFile.url}"

class Tasks(models.Model):
    title = models.CharField(max_length=255)
    amount = models.FloatField()
    description = models.TextField()

    @property
    def amounts(self):
        return f"${self.amount}"

    def __str__(self):
        return f"{self.title}"

class UserTasks(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos/")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

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


