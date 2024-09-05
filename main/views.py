from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import SignupForm, VerificatonForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
import json
from .models import User, UserTasks, Documents, Token, Tasks


def load(request):
    json_file_path = 'tasks.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            Tasks.objects.create(title=item['title'], amount=0.7, description=item['description'])
    return JsonResponse({'success': True, 'message': 'Tasks loaded successfully'}, status=200)

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    form = SignupForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': True, 'message': 'Email already in use'}, status=400)
    user = User.objects.create(email=email, password=password)
    token = Token.objects.create(user=user)  
    return JsonResponse({'success': True, 'message': 'Account created successfully', 'token': token.key}, status=200)

def login(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    form = SignupForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    user = authenticate(email=email, password=password)
    if user is None:
        return JsonResponse({'error': True, 'message': 'Invalid email or password'}, status=400)
    old_token = Token.objects.get(user=user)
    old_token.delete()
    new_token = Token.objects.create(user=user).key
    tasks = UserTasks.objects.get(user=user)
    pending_tasks_count = UserTasks.objects.filter(user=user, status='pending').count()
    completed_tasks_count = UserTasks.objects.filter(user=user, status='completed').count()
    account = {
        'email': user.email,
        'earned': user.earned,
        'full_name': user.get_full_name,
    }
    tasks = {
        'pending_tasks': pending_tasks_count,
        'completed_tasks': completed_tasks_count,
        'total_tasks_taken': pending_tasks_count + completed_tasks_count,
    }
    return JsonResponse({'success': True, 'token': new_token, 'account': account, 'tasks': tasks}, status=200)
