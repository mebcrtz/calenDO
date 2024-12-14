from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='calendo-dashboard'),
    path('todo/', views.todo_index, name='todo_index'),
    path('todo/create-task/', views.create_task, name='create_task'),
    path('todo/task-detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('todo/update-task/', views.update_task, name='update_task'),

    path('calendar/', views.calendar_index, name='calendar_index'),
    path('calendar/<slug:schedule_name>/', views.calendar_index, name='schedule_detail'),
    path('create-schedule/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:pk>/add-item/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/item/<int:pk>/update/', views.update_item_details, name='update_item_details'),
]