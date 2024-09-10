import json, requests
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import LoginForm, SignupForm, VerificatonForm
from .models import User, UserTasks, Documents, Token, Tasks, History



def load(request):
    json_file_path = 'tasks.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            Tasks.objects.create(title=item['title'], amount=0.7, description=item['description'])
    return JsonResponse({'success': True, 'message': 'Tasks loaded successfully'}, status=200)

class UserView:
    def __init__(self, user):
        self.user = user

    def getUser(self):
        user_info = self.getUserInfo()
        status = self.getUserStatus()
        token = self.getUserToken()
        tasks = self.getUserTasks()
        return user_info, status, tasks, token

    def getUserInfo(self):
        user = self.user    
        user_info = {
            'name': f'{user.first_name} {user.last_name}',
            'email': user.email,
            'balance': user.balance,
            'isVerify': user.is_verify,
        }
        return user_info

    def getUserToken(self):
        token, created = Token.objects.get_or_create(user=self.user)
        if not created:
            token.delete()
            token = Token.objects.create(user=self.user)
        return token.key
    
    def getUserTasks(self):
        user = self.user
        today = timezone.now().date()
        tasks_today = UserTasks.objects.filter(user=user, created_at__date=today).count()
        tasks_remaining = user.daily_task - tasks_today
        user_task_ids = UserTasks.objects.filter(user=self.user).values_list('task_id', flat=True)
        tasks_available = Tasks.objects.exclude(id__in=user_task_ids).order_by('?')[:tasks_remaining]
        tasks = list(tasks_available.values())
        return tasks
    
    def getUserStatus(self):
        user = self.user
        pendingTasks = UserTasks.objects.filter(user=user, status='pendingTasks').count()
        passedTasks = UserTasks.objects.filter(user=user, status='passedTasks').count()
        failedTasks = UserTasks.objects.filter(user=user, status='failedTasks').count()        
        status = {
            'pendingTasks': pendingTasks,
            'passedTasks': passedTasks,
            'failedTasks': failedTasks,
        }   
        return status
    
    def getUserHistory(self):
        user = self.user
        history = History.objects.filter(user=user).all()
        history = list(history.values())
        return history
    
    @csrf_exempt
    @staticmethod
    def getUserData(request):
        if request.method != "POST":
            return redirect('https://app.aiannotaion.site')
        refresh = request.POST.get('refresh')
        token_key = request.POST.get('token')
        try:
            token = Token.objects.get(key=token_key)
            user = token.user
        except Token.DoesNotExist:
            return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
        user = UserView(user)
        user_info = user.getUserInfo()
        status = user.getUserStatus()
        tasks = user.getUserTasks()
        if(refresh=="false"):
            token_key = user.getUserToken()
        return JsonResponse({'success': True, 'user': user_info, 'status': status, 'tasks': tasks, 'token': token_key}, status=200)

@csrf_exempt
def signup(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    form = SignupForm(request.POST)
    if form.is_valid() != True:
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': True, 'message': 'Email already in use'}, status=400)
    user = User.objects.create(email=email, password=password)
    user, status, tasks, token = UserView(user).getUser()
    return JsonResponse({'success': True, 'user': user, 'status': status, 'tasks': tasks, 'token': token}, status=200)

@csrf_exempt
def signin(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    form = LoginForm(request.POST)
    if form.is_valid() != True:
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=200)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    user = authenticate(username=email, password=password)
    if user is None:
        return JsonResponse({'error': True, 'message': 'Invalid email or password'}, status=400)
    user, status, tasks, token = UserView(user).getUser()
    return JsonResponse({'success': True, 'user': user, 'status': status, 'tasks': tasks, 'token': token}, status=200)

@csrf_exempt
def status(request):
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    status = UserView(user).getUserStatus()
    return JsonResponse({'success': True, 'status': status}, status=200)

@csrf_exempt
def tasks(request):
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    tasks = UserView(user).getUserTasks()
    return JsonResponse({'success': True, 'tasks': tasks}, status=200)

@csrf_exempt
def history(request):
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    history = UserView(user).getUserHistory()
    return JsonResponse({'success': True, 'history': history}, status=200)

@csrf_exempt
def submit(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    task_id = request.POST.get('taskId')
    photo_file = request.FILES.get('photo')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Logout and try again'}, status=400)
    if photo_file is None or task_id is None:
        return JsonResponse({'error': True, 'message': 'Invalid data, try again'}, status=400)
    user = Token.objects.get(key=token_key).user
    tasks = Tasks.objects.get(id=task_id)
    UserTasks.objects.create(user=user, task=tasks, created_at=timezone.now, photo=photo_file)
    return JsonResponse({'success': True, 'message': 'Task submitted successfully'}, status=200)

@csrf_exempt
def withdraw(request):
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    amount = request.POST.get('amount')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Logout and try again'}, status=400)
    user = Token.objects.get(key=token_key).user
    if amount is None or float(amount) > user.balance:
        return JsonResponse({'error': True, 'message': 'Invalid data, try again'}, status=400)
    description = ""
    print(user.balance)
    user.balance = user.balance - float(amount)
    user.save()
    print(user.balance)
    History.objects.create(user=user, title=amount, description=description, action='pendingDebit')
    return JsonResponse({'success': True}, status=200)

@csrf_exempt
def bankList(request):
    url = "https://api.paystack.co/bank"
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid auth token'}, status=400)
    headers = {
        "Authorization": "Bearer "
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data['status'])
    if data['status'] == True:
        return JsonResponse({'success': True, 'data': data['data']}, status=200)
    return JsonResponse({'error': True}, status=400)

@csrf_exempt
def bankResolve(request):
    url = "https://api.paystack.co/bank/resolve"
    if request.method != "POST":
        return redirect('https://app.aiannotaion.site')
    bank_code = request.POST.get('bank_code')
    account_number = request.POST.get('account_number')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid auth token'}, status=400)
    if bank_code is None or account_number is None or len(str(account_number)) < 10:
        return JsonResponse({'error': True, 'message': 'Invalid data parse'}, status=400)
    params = {
        "account_number": account_number,
        "bank_code": bank_code
    }
    headers = {
        "Authorization": "Bearer "
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['status'] == True:
        return JsonResponse({'success': True, 'data': data['data']}, status=200)
    return JsonResponse({'error': True}, status=400)

@csrf_exempt
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
