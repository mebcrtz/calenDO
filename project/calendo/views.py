from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse

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



def calendar(request):
    return HttpResponse("This is the calendar page")

def todo(ListView):
    return HttpResponse("This is the todo page")