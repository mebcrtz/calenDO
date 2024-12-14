from django.contrib import admin
from django.urls import path, include
from calendo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='calendo-dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('todo/', views.todo_index, name='todo_index'),
    path('todo/create-task/', views.create_task, name='create_task'),
    path('calendar/', views.calendar_index, name='calendar_index'),
    path('accounts/', include('django.contrib.auth.urls')),
]