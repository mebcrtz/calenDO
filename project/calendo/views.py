from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from .models import Task, Schedule, Event
from .forms import TaskForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('calendo-dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('calendo-dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    # Your dashboard logic here
    return render(request, 'dashboard.html')

@login_required
def todo_index(request):
    # Organize tasks by section
    tasks = Task.objects.all()
    sections_and_tasks = {}
    for task in tasks:
        if task.section not in sections_and_tasks:
            sections_and_tasks[task.section] = []
        sections_and_tasks[task.section].append(task)
    return render(request, 'todo/todo-index.html', {'sections_and_tasks': sections_and_tasks})

@login_required
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
    return render(request, 'todo/create-task.html', {'form': form})

@login_required
def calendar_index(request):
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, 'calendar/calendar-index.html', {'schedules': schedules})

from django.shortcuts import render
from .models import Event

def calendar(request):
    events = Event.objects.all()
    return render(request, 'calendar.html', {'events': events})