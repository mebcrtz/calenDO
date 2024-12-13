from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world")

def calendar(request):
    return HttpResponse("This is the calendar page")

def todo(request):
    return HttpResponse("This is the todo page")