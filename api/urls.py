from django.urls import path
from . import views

urlpatterns = [
    # path('load/', views.load, name="Load")
    path('login/', views.signin, name="signin"),
    path('signup/', views.signup, name="Signup"),
    path('tasks/', views.tasks, name="tasks"),
    path('status/', views.status, name="status"),
    path('submit/', views.submit, name="submit"),
    path('user/', views.UserView.getUserData, name="getuser"),
    path('verification/', views.verification, name="verification"),
]
