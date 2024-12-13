from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='calendo-index'),
    path('calendar/', views.calendar, name='calendo-calendar'),
    path('todo/', views.todo, name='calendo-todo'),
    path('create-task/', views.create_task, name='create_task'),
    path('task-detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('update-task/', views.update_task, name='update_task'),
]