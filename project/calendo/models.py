from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
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


class Note(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.task.task_name} at {self.timestamp}"


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


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.title