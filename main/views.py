from django.http import JsonResponse
from django.views.decorators.http import require_POST
from api.forms import LoginForm, SignupForm, VerificatonForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
import json
from api.models import User, UserTasks, Documents, Token, Tasks


def load(request):
    json_file_path = 'tasks.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            Tasks.objects.create(title=item['title'], amount=0.7, description=item['description'])
    return JsonResponse({'success': True, 'message': 'Tasks loaded successfully'}, status=200)

def home(request):
    return render(request, 'home.html')

def getuser(request=None, user=None):
    if not request.user.is_authenticated:
        return JsonResponse({'error': True, 'message': 'Login required'}, status=400)
    user = request.user
    pending_tasks_count = UserTasks.objects.filter(user=user, status='pending').count()
    completed_tasks_count = UserTasks.objects.filter(user=user, status='completed').count()
    
    today = timezone.now().date()
    tasks_today = UserTasks.objects.filter(user=user, created_at__date=today).count()
    if tasks_today >= 3:
        return JsonResponse({'error': True, 'message': 'Task limit of 3 per day reached'}, status=400)
    tasks_remaining = 3 - tasks_today
    tasks_available = Tasks.objects.exclude(id__in=UserTasks.objects.filter(user=user).values_list('task_id', flat=True)).order_by('?')[:tasks_remaining]
    tasks = list(tasks_available.values())
    user = {
        'name': user.first_name,
        'email': user.email,
        'balance': user.balance,
        'isVerify': user.is_verify,
    }
    status = {
        'pending_tasks': pending_tasks_count,
        'completed_tasks': completed_tasks_count,
        'total_tasks_taken': pending_tasks_count + completed_tasks_count,
    }
    if request is not None:
        return JsonResponse({'success': True, 'user': user, 'status': status, 'tasks': tasks}, status=200)
    return user, status, tasks_available

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
    user, status, tasks = getuser(user=user)
    return JsonResponse({'success': True, 'user': user, 'status': status, 'tasks': tasks}, status=200)

def login(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    form = LoginForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    user = authenticate(email=email, password=password)
    if user is None:
        return JsonResponse({'error': True, 'message': 'Invalid email or password'}, status=400)
    login(request, user)
    user, status, tasks = getuser(user=user)
    return JsonResponse({'success': True, 'user': user, 'status': status, 'tasks': tasks}, status=200)

def status(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': True, 'message': 'Login required'}, status=400)
    user = request.user
    pendingTasks = UserTasks.objects.filter(user=user, status='pendingTasks').count()
    passedTasks = UserTasks.objects.filter(user=user, status='passedTasks').count()
    failedTasks = UserTasks.objects.filter(user=user, status='failedTasks').count()
    tasks = {
        'pendingTasks': pendingTasks,
        'passedTasks': passedTasks,
        'failedTasks': failedTasks,
    }
    return JsonResponse({'success': True, 'tasks': tasks}, status=200)

def tasks(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': True, 'message': 'Login required'}, status=400)
    user = request.user
    today = timezone.now().date()
    tasks_today = UserTasks.objects.filter(user=user, created_at__date=today).count()
    if tasks_today >= 3:
        return JsonResponse({'error': True, 'message': 'Task limit of 3 per day reached'}, status=400)
    tasks_remaining = 3 - tasks_today
    tasks_available = Tasks.objects.exclude(id__in=UserTasks.objects.filter(user=user).values_list('task_id', flat=True)).order_by('?')[:tasks_remaining]
    tasks = list(tasks_available.values())
    return JsonResponse({'success': True, 'tasks': tasks}, status=200)

def submit(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    task_id = request.POST.get('task_id')
    photo_file = request.FILES.get('photo')
    if not request.user.is_authenticated:
        return JsonResponse({'error': True, 'message': 'Login required'}, status=400)
    user = request.user
    if not user.is_verify:
        return JsonResponse({'error': True, 'message': 'Please verify your account first'}, status=400)
    if photo_file is None or task_id is None or not Tasks.objects.filter(id=task_id).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Data Parse'}, status=400)
    tasks = Tasks.objects.get(id=task_id)
    UserTasks.objects.create(user=user, task=tasks, created_at=timezone.now, photo=photo_file)
    return JsonResponse({'success': True}, status=200)

def verification(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    if not request.user.is_authenticated:
        return JsonResponse({'error': True, 'message': 'Login required'}, status=400)
    user = request.user
    form = VerificatonForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    user.is_verify = True
    user.save()
    return JsonResponse({'success': True}, status=200)

