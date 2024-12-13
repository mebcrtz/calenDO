from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from .forms import *
from .models import *

# Create your views here.
def index(request):
    # Organize tasks by section
    tasks = Task.objects.all()
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/index.html', {'sections_and_tasks': sections_and_tasks})

def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calendo-index')
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = TaskForm()
    return render(request, 'modal.html', {'form': form})

def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    task_data = {
        "task_name": task.task_name,
        "description": task.description,
        # "notes": task.notes.split("\\n") if task.notes else [],
        "due_date": task.due_date.strftime('%Y-%m-%d'),
        "section": task.section,
        "priority": task.priority,
    }
    return JsonResponse(task_data)

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
            return redirect('calendo-index')
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def calendar(request):
    return HttpResponse("This is the calendar page")

def todo(ListView):
    return HttpResponse("This is the todo page")