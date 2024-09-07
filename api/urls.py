from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="Home"),
    path('signup/', views.signup, name="Signup"),
    # path('load/', views.load, name="Load")
]
