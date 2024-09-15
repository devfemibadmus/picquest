from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^app.*$', views.app, name="app"),
    re_path(r'^.*$', views.home, name="Home"),
]
