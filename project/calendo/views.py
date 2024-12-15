from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from datetime import time
from django.utils import timezone
from django.contrib import messages

from .forms import *
from .models import Task, Note
# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

'''TO-DO VIEWS'''

def todo_index(request):
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
            return redirect('todo_index')
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TaskForm()
    return render(request, 'modal.html', {'form': form})

def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    notes = Note.objects.filter(task=task).order_by('-timestamp')
    notes_data = [{'content': note.content, 'timestamp': note.timestamp.strftime('%B %d, %Y %I:%M %p')} for note in notes]
    task_data = {
        'task_name': task.task_name,
        'description': task.description,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'section': task.section,
        'priority': task.priority,
        'notes': notes_data
    }
    return JsonResponse(task_data)

def add_note(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        content = request.POST.get('notes')
        task = Task.objects.get(id=task_id)
        note = Note.objects.create(task=task, content=content, timestamp=timezone.now())
        return redirect('todo_index')
    return HttpResponse('Invalid request', status=400)

def delete_task(request, task_id):
    if request.method == 'DELETE':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return HttpResponse(status=204)
    return HttpResponse('Invalid request', status=400)

def update_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        if not task_id:
            return JsonResponse({"error": "Task ID is missing"}, status=400)

        try:
            task = Task.objects.get(id=task_id)
            task.task_name = request.POST.get("task_name")
            task.description = request.POST.get("description")
            task.due_date = request.POST.get("due_date")
            task.section = request.POST.get("section")
            task.priority = request.POST.get("priority")
            task.save()
            return redirect('todo_index')
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def set_priority(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        priority = request.POST.get('priority')
        try:
            task = Task.objects.get(id=task_id)
            task.priority = priority
            task.save()
            return redirect('todo_index')
        except Task.DoesNotExist:
            return HttpResponse('Task not found', status=404)
    return HttpResponse('Invalid request', status=400)


'''CALENDAR VIEWS'''

def calendar_index(request):
    schedules = Schedule.objects.filter(user=request.user)
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render(request, "calendar/calendar-index.html", {"schedules": schedules})

def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    schedules = Schedule.objects.filter(user=request.user)  # For sidebar
    items = schedule.items.prefetch_related('occurrences__days_of_week')  # Prefetch occurrences and days
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Prepare occurrences with days
    for item in items:
        for occurrence in item.occurrences.all():
            occurrence.days = [day.name for day in occurrence.days_of_week.all()]  # Preprocess days as a list of names

    return render(request, "calendar/schedule-detail.html", {
        "schedule": schedule,
        "schedules": schedules,
        "items": items,
        "days_of_week": days_of_week,
    })

def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, "schedule-list.html", {"schedules": schedules})

def create_schedule(request):
    if request.method == "POST":
        schedule_name = request.POST.get("schedule_name")
        if schedule_name:
            Schedule.objects.create(
                schedule_name=schedule_name,
                user=request.user
            )
            return redirect("calendar_index")  # Replace with the name of your schedule list view
        else:
            # Return an error message or redirect with an error
            return render(request, "create_schedule.html", {"error": "Schedule name is required."})
    else:
        # Render a form page if accessed via GET
        return render(request, "create_schedule.html")
    
def add_schedule_item(request, pk):
    if request.method == "POST":
        schedule = get_object_or_404(Schedule, pk=pk, user=request.user)

        # Get form data
        item_name = request.POST.get("itemName")
        item_type = request.POST.get("itemType")
        notes = request.POST.get("notes", "")
        days = request.POST.getlist("days[]")
        start_times = request.POST.getlist("startTime[]")
        end_times = request.POST.getlist("endTime[]")

        # Create the Item
        item = Item.objects.create(
            schedule=schedule,
            item_name=item_name,
            type=item_type,
            notes=notes
        )

        # Process each time block once
        for start_time, end_time in zip(start_times, end_times):
            # Create a single ItemOccurrence for each time range
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            # Add all selected days to this occurrence
            for day_name in days:
                day_of_week, _ = DayOfWeek.objects.get_or_create(name=day_name)
                occurrence.days_of_week.add(day_of_week)

        messages.success(request, "Item added successfully!")
        return redirect("schedule_detail", pk=pk)

    return redirect("schedule_detail", pk=pk)

def update_item(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == "POST":
        item_name = request.POST.get("itemName")
        item_type = request.POST.get("item_type")
        item_notes = request.POST.get("item_notes")

        # Update the item fields
        item.item_name = item_name
        item.type = item_type
        item.notes = item_notes
        item.save()

        messages.success(request, "Item updated successfully!")
        return redirect("schedule_detail", pk=item.schedule.id)
    return redirect("schedule_detail", pk=item.schedule.id)

def update_item_details(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == "POST":
        # Debugging: Print the POST data
        print(request.POST)

        item_name = request.POST.get("itemName")
        item_type = request.POST.get("itemType")
        item_notes = request.POST.get("notes", "")

        if not item_name:  # Check if the item name is empty
            messages.error(request, "Item name cannot be empty!")
            return redirect("schedule_detail", pk=item.schedule.id)

        # Update the Item fields
        item.item_name = item_name
        item.type = item_type
        item.notes = item_notes
        item.save()

        # Clear existing occurrences
        item.occurrences.all().delete()

        # Add new occurrences
        days = request.POST.getlist("days[]")
        start_times = request.POST.getlist("startTime[]")
        end_times = request.POST.getlist("endTime[]")

        for start_time, end_time in zip(start_times, end_times):
            occurrence = ItemOccurrence.objects.create(
                item=item,
                start_time=start_time,
                end_time=end_time
            )
            for day_name in days:
                day_of_week, _ = DayOfWeek.objects.get_or_create(name=day_name)
                occurrence.days_of_week.add(day_of_week)

        messages.success(request, "Item updated successfully!")
        return redirect("schedule_detail", pk=item.schedule.id)

    return redirect("schedule_detail", pk=item.schedule.id)
