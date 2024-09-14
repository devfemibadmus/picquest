from django.urls import re_path, path
from . import views

urlpatterns = [
    path('app/', views.app, name="app"),
    re_path(r'^.*$', views.home, name="Home"),
]
