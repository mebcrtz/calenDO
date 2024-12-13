from django.urls import path
from . import views

urlpatterns = [
    path('todo/', views.todo_index, name='todo_index'),
    path('todo/create-task/', views.create_task, name='create_task'),
    path('todo/task-detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('todo/update-task/', views.update_task, name='update_task'),

    path('calendar/', views.calendar, name='calendo-calendar'),
    path('todo/', views.todo, name='calendo-todo'),

]