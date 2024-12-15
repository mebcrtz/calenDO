from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class Task(models.Model):
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    section = models.CharField(max_length=255)
    priority = models.CharField(max_length=50)

class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Schedule(models.Model):
    schedule_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_name

class Item(models.Model):
    EVENT_TYPE_CHOICES = [
        ('event', 'Event'),
        ('class', 'Class'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

class DayOfWeek(models.Model):
    name = models.CharField(max_length=9, unique=True)  # Monday, Tuesday, etc.

    def __str__(self):
        return self.name

class ItemOccurrence(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="occurrences")
    days_of_week = models.ManyToManyField(DayOfWeek)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        days = ', '.join(day.name for day in self.days_of_week.all())
        return f"{self.item.item_name} ({days}: {self.start_time} - {self.end_time})"