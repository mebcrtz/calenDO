from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='calendo-dashboard'),
    path('todo/', views.todo_index, name='todo_index'),
    path('todo/create-task/', views.create_task, name='create_task'),
    path('todo/task-detail/<int:task_id>/', views.task_detail, name='task_detail'),
    path('todo/update-task/', views.update_task, name='update_task'),
    path('list-view/', views.list_view, name='list-view'),
    path('update-section/<str:section_name>/', views.update_section, name='update_section'),
    path('update-task/<int:task_id>/', views.update_task, name='update_task'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),

    path('calendar/', views.calendar_index, name='calendar_index'),
    path('calendar/<slug:schedule_name>/', views.calendar_index, name='schedule_detail'),
    path('create-schedule/', views.create_schedule, name='create_schedule'),
    path('schedule/<slug:schedule_name>/add-item/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/<slug:schedule_name>/item/<int:pk>/update/', views.update_item_details, name='update_item_details'),
    path('item/remove/<int:pk>/', views.remove_schedule_item, name='remove_schedule_item'),
    path('calendar/<slug:schedule_name>/delete/', views.delete_schedule, name='delete_schedule'),
    path('calendar/<slug:schedule_name>/export/<str:file_type>/', views.export_schedule, name='export_schedule'),
]