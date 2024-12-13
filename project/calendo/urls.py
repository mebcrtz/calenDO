from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='calendo-index'),
    path('calendar/', views.calendar, name='calendo-calendar'),
    path('todo/', views.todo, name='calendo-todo'),
    path('create-task/', views.create_task, name='create_task'),
]