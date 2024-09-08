from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="Home"),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="Signup"),
    path('getuser/', views.getuser, name="getuser"),
    path('tasks/', views.tasks, name="tasks"),
    path('status/', views.status, name="status"),
    path('submit/', views.submit, name="submit"),
    path('verification/', views.verification, name="verification"),
]
