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
    path('schedule/<slug:schedule_name>/add-item/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/<slug:schedule_name>/item/<int:pk>/update/', views.update_item_details, name='update_item_details'),
    path('item/remove/<int:pk>/', views.remove_schedule_item, name='remove_schedule_item'),
    path('calendar/<slug:schedule_name>/delete/', views.delete_schedule, name='delete_schedule'),
    path('calendar/<slug:schedule_name>/export/<str:file_type>/', views.export_schedule, name='export_schedule'),

    path('signup/', views.signup_page, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),

]