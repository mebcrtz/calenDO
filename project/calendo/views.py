from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import *
from .models import *

# Create your views here.
def index(request):
    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')

    context = {
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'todo/index.html', context)

def calendar(request):
    return HttpResponse("This is the calendar page")

def todo(ListView):
    return HttpResponse("This is the todo page")