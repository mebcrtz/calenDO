from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='calendo-index'),
    path('calendar/', views.calendar, name='calendo-calendar'),
    path('todo/', views.todo, name='calendo-todo'),
]