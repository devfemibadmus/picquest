from django.urls import path
from . import views

urlpatterns = [
    # path('load/', views.load, name="Load"),
    path('tasks/', views.tasks, name="tasks"),
    path('signin/', views.signin, name="signin"),
    path('signup/', views.signup, name="Signup"),
    path('status/', views.status, name="status"),
    path('submit/', views.submit, name="submit"),
    path('history/', views.history, name="history"),
    path('withdraw/', views.withdraw, name="withdraw"),
    path('bankList/', views.bankList, name="bankList"),
    path('bankResolve/', views.bankResolve, name="bankResolve"),
    path('getuser/', views.UserView.getUserData, name="getuser"),
    path('verification/', views.verification, name="verification"),
]
