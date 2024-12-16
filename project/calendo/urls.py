from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='calendo-dashboard'),
    path('todo/', views.todo_index, name='todo_index'),
    path('todo/create-task/', views.create_task, name='create_task'),
    path('todo/task-detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('todo/update-task/', views.update_task, name='update_task'),
    path('set-priority/', views.set_priority, name='set_priority'),
    path('add-note/', views.add_note, name='add_note'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),

    path('calendar/', views.calendar_index, name='calendar_index'),
    path('schedule/<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('create-schedule/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:pk>/add-item/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/<int:pk>/update-item/', views.update_item, name='update_item'),
    path('schedule/item/<int:pk>/update/', views.update_item, name='update_item'),
]