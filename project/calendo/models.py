from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)
    section = models.CharField(max_length=200, null=True, blank=True)
    priority = models.CharField(max_length=200, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name
    
    class Meta:
        ordering = ['status']