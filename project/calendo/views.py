import io
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from datetime import time
from django.contrib import messages
from django.utils.text import slugify
from django.urls import reverse
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import *
from .models import *

# Dashboard View
def dashboard(request):
    return render(request, 'dashboard.html')

'''TO-DO VIEWS'''

def todo_index(request):
    # Organize tasks by section
    tasks = Task.objects.all()
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/todo-index.html', {'sections_and_tasks': sections_and_tasks})


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created successfully!")
            return redirect('todo_index')  # Redirect to avoid resubmission
        else:
            messages.error(request, "Failed to create task. Please check the form.")
            return redirect('todo_index')
    else:
        form = TaskForm()
    return render(request, 'modal.html', {'form': form})


def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task_data = {
        "task_name": task.task_name,
        "description": task.description,
        "due_date": task.due_date.strftime('%Y-%m-%d'),
        "section": task.section,
        "priority": task.priority,
    }
    return JsonResponse(task_data)


@csrf_exempt
def update_task(request, task_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_title = data.get('new_title')
        new_desc = data.get('new_desc')
        new_date = data.get('new_date')
        try:
            task = Task.objects.get(id=task_id)
            if new_title:
                task.task_name = new_title
            if new_desc:
                task.description = new_desc
            if new_date:
                task.due_date = new_date
            task.save()
            return JsonResponse({'status': 'success'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Task not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_task(request, task_id):
    if request.method == 'DELETE':
        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return JsonResponse({'status': 'success'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Task not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

def list_view(request):
    # Organize tasks by section
    tasks = Task.objects.all()
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/list-view.html', {'sections_and_tasks': sections_and_tasks})


@csrf_exempt
def update_section(request, section_name):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_title = data.get('new_title')
        try:
            section = Section.objects.get(name=section_name)
            section.name = new_title
            section.save()
            return JsonResponse({'status': 'success'})
        except Section.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Section not found'}, status=404)
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'}, status=400)

'''CALENDAR VIEWS'''

def get_current_week_dates():
    """Get the dates for the current week's Monday through Sunday."""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
    return {
        day_name: (start_of_week + timedelta(days=i)).date()
        for i, day_name in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    }

def calendar_index(request, schedule_name=None):
    schedules = Schedule.objects.filter(user=request.user)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    first_schedule = schedules.first()
    schedule = first_schedule if schedule_name is None else get_object_or_404(Schedule, slug=schedule_name, user=request.user)
    items = schedule.items.prefetch_related('occurrences__days_of_week') if schedule else []

    # Get current week dates
    current_week_dates = get_current_week_dates()

    # Prepare items with exact dates for occurrences
    event_list = []
    for item in items:
        for occurrence in item.occurrences.all():
            occurrence.days = [day.name for day in occurrence.days_of_week.all()]
            for day_name in occurrence.days:
                if day_name in current_week_dates:
                    event_date = current_week_dates[day_name]
                    event_list.append({
                        'title': item.item_name,
                        'start': f"{event_date}T{occurrence.start_time}",
                        'end': f"{event_date}T{occurrence.end_time}",
                    })

    return render(request, "calendar/calendar-index.html", {
        "schedules": schedules,
        "schedule": schedule,
        "first_schedule": first_schedule,
        "items": items,
        "days_of_week": days_of_week,
        "events": event_list,  # Pass the calculated events to the template
    })


def create_schedule(request):
    if request.method == "POST":
        schedule_name = request.POST.get("schedule_name")
        if schedule_name:
            Schedule.objects.create(
                schedule_name=schedule_name,
                user=request.user
            )
            messages.success(request, "Schedule created successfully!")
            return redirect("calendar_index")
        else:
            messages.error(request, "Schedule name is required.")
            return redirect("calendar_index")
    return render(request, "create_schedule.html")


def add_schedule_item(request, schedule_name):
    schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)

    if request.method == "POST":
        item_name = request.POST.get("itemName")
        item_type = request.POST.get("itemType")
        notes = request.POST.get("notes", "")
        days = request.POST.getlist("days[]")
        start_times = request.POST.getlist("startTime[]")
        end_times = request.POST.getlist("endTime[]")

        if not item_name or not days or not start_times or not end_times:
            messages.error(request, "All fields are required!")
            return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))

        item = Item.objects.create(
            schedule=schedule,
            item_name=item_name,
            type=item_type,
            notes=notes
        )

        for start_time, end_time in zip(start_times, end_times):
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            for day in days:
                day_of_week, _ = DayOfWeek.objects.get_or_create(name=day)
                occurrence.days_of_week.add(day_of_week)

        messages.success(request, "Item added successfully!")
        return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))

    return redirect(reverse('schedule_detail', kwargs={'schedule_name': schedule.slug}))


def update_item_details(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = get_object_or_404(Item, id=item_id)

        item.item_name = request.POST.get('itemName')
        item.type = request.POST.get('itemType')
        item.notes = request.POST.get('notes')
        item.save()

        item.occurrences.all().delete()
        days = request.POST.getlist('days[]')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')

        if days and start_time and end_time:
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            for day in days:
                day_of_week, _ = DayOfWeek.objects.get_or_create(name=day)
                occurrence.days_of_week.add(day_of_week)

        messages.success(request, 'Item updated successfully!')
        return redirect("schedule_detail", schedule_name=item.schedule.slug)


def remove_schedule_item(request, pk):
    item = get_object_or_404(Item, pk=pk, schedule__user=request.user)
    if request.method == "POST":
        schedule_name = item.schedule.slug
        item.delete()
        messages.success(request, "Item removed successfully!")
        return redirect("schedule_detail", schedule_name=schedule_name)
    return redirect("schedule_detail", schedule_name=item.schedule.slug)


def delete_schedule(request, schedule_name):
    if request.method == "POST":
        schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)
        schedule.delete()
        messages.success(request, f"The schedule '{schedule.schedule_name}' has been deleted.")
        return redirect("calendar_index")
    else:
        messages.error(request, "Invalid request method.")
        return redirect("calendar_index")


def export_schedule(request, schedule_name, file_type):
    schedule = get_object_or_404(Schedule, slug=schedule_name, user=request.user)
    items = schedule.items.all()

    if file_type == 'pdf':
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"Schedule: {schedule.schedule_name}")
        y = 780
        for item in items:
            p.drawString(100, y, f"{item.item_name}: {item.notes}")
            y -= 20
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{schedule.schedule_name}.pdf")

    elif file_type in ['jpg', 'png']:
        image_format = 'JPEG' if file_type == 'jpg' else 'PNG'
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        y = 50
        d.text((10, 10), f"Schedule: {schedule.schedule_name}", fill=(0, 0, 0), font=font)
        for item in items:
            d.text((10, y), f"{item.item_name}: {item.notes}", fill=(0, 0, 0), font=font)
            y += 20

        buffer = io.BytesIO()
        img.save(buffer, format=image_format)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{schedule.schedule_name}.{file_type}")

    else:
        messages.error(request, "Invalid file type.")
        return redirect("schedule_detail", schedule_name=schedule_name)
