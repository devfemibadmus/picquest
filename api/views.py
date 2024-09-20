import json, requests, time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from .forms import SigninForm, SignupForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import User, UserTask, Document, Token, Task, PayOut, VerificationFee

sk_token = settings.SK_TOKEN
app_url = '/app/'

def load(request):
    json_file_path = 'tasks.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            Task.objects.create(title=item['title'], amount=0.7, description=item['description'])
    return JsonResponse({'success': True, 'message': 'Tasks loaded successfully'}, status=200)

class UserView:
    def __init__(self, user):
        self.user = user

    def getUser(self):
        user_info = self.getUserInfo()
        token = self.getUserToken()
        tasks = self.getUserTasks()
        return user_info, tasks, token

    def getUserInfo(self):
        user = self.user
        referral = None
        if user.referral is not None:
            referral = user.referral.email
        user_info = {
            'name': user.first_name,
            'email': user.email,
            'rearns': user.rearns,
            'balance': user.balance,
            'referral': referral,
            'hasPaid': user.hasPaid,
            'isVerify': user.is_verify,
            'passedTasks': user.passTasks,
            'failedTasks': user.failTasks,
            'pendingTasks': user.pendTasks,
            'minWithdraw': user.minWithdraw,
            'documentSubmitted': user.documentSubmitted,
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
        tasks_today = UserTask.objects.filter(user=user, created_at__date=today).count()
        tasks_remaining = user.daily_task - tasks_today
        user_task_ids = UserTask.objects.filter(user=self.user).values_list('task_id', flat=True)
        tasks_available = Task.objects.exclude(id__in=user_task_ids).order_by('?')[:tasks_remaining]
        tasks = list(tasks_available.values())
        return tasks
        
    def getUserPayOuts(self):
        user = self.user
        payouts = PayOut.objects.filter(user=user).all()
        payouts = list(payouts.values())
        return payouts
    
    @csrf_exempt
    @staticmethod
    def getUserData(request):
        if request.method != "POST":
            return redirect(app_url)
        refresh = request.POST.get('refresh')
        token_key = request.POST.get('token')
        if token_key is None or refresh is None:
            return JsonResponse({'error': True, 'message': 'Invalid data parse'}, status=400)
        if not Token.objects.filter(key=token_key).exists():
            return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
        user = Token.objects.get(key=token_key).user
        user = UserView(user)
        user_info = user.getUserInfo()
        tasks = user.getUserTasks()
        if(not refresh):
            print(refresh)
            token_key = user.getUserToken()
        return JsonResponse({'success': True, 'user': user_info, 'tasks': tasks, 'token': token_key}, status=200)


@csrf_exempt
def signup(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    form = SignupForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    fullName = form.cleaned_data['fullName']
    referral_email = request.POST.get('referral')
    referral = None
    if referral_email and User.objects.filter(email=referral_email).exists():
        referral = User.objects.get(email=referral_email)
        PayOut.objects.create(user=referral, amount='0.03', action='referral')
    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': True, 'message': 'Email already in use'}, status=400)
    user = User(email=email, first_name=fullName, referral=referral)
    user.set_password(password)
    user.save()
    user_data, status, tasks, token = UserView(user).getUser()
    return JsonResponse({'success': True, 'user': user_data, 'tasks': tasks, 'token': token}, status=200)

@csrf_exempt
def signin(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    form = SigninForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': True, 'message': 'Invalid data'}, status=400)
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']
    user = authenticate(username=email, password=password)
    if user is None:
        return JsonResponse({'error': True, 'message': 'Invalid email or password'}, status=400)
    user_data, tasks, token = UserView(user).getUser()
    return JsonResponse({'success': True, 'user': user_data, 'tasks': tasks, 'token': token}, status=200)

@csrf_exempt
def tasks(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    tasks = UserView(user).getUserTasks()
    return JsonResponse({'success': True, 'tasks': tasks}, status=200)

@csrf_exempt
def payouts(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    payouts = UserView(user).getUserPayOuts()
    return JsonResponse({'success': True, 'payouts': payouts}, status=200)

@csrf_exempt
def payment(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid Authorization token'}, status=400)
    user = Token.objects.get(key=token_key).user
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {sk_token}", "Content-Type": "application/json"}
    data = {"email": user.email, "amount": 2100, "callback_url": f"{request.scheme}://{request.get_host()}/api/v1/callback/{user.email}/"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        data = response.json()
        authorization_url = data['data']['authorization_url']
        paymentName = authorization_url.split("/")[-1]
        payment = VerificationFee.objects.filter(user=user, reference__isnull=True).first()
        if payment is None:
            payment = VerificationFee.objects.create(user=user, name=paymentName)
        else:
            payment.name = paymentName
            payment.save()
        return JsonResponse({'success': True, 'paymentUrl': authorization_url}, status=200)
    return JsonResponse({'error': True}, status=400)

@csrf_exempt
def callback(request, email):
    reference = request.GET.get('reference')
    if reference and email:
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {sk_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['message'] == 'Verification successful':
                user = User.objects.get(email=email)
                user.hasPaid = True
                user.save()
                payment = VerificationFee.objects.filter(user=user, reference__isnull=True).first()
                payment.reference = reference
                payment.save()
    return redirect(app_url)

@csrf_exempt
def submit(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    task_id = request.POST.get('taskId')
    photo_file = request.FILES.get('photo')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Logout and try again'}, status=400)
    if photo_file is None or task_id is None:
        return JsonResponse({'error': True, 'message': 'Invalid data, try again'}, status=400)
    user = Token.objects.get(key=token_key).user
    tasks = Task.objects.get(id=task_id)
    UserTask.objects.create(user=user, task=tasks, created_at=timezone.now, photo=photo_file)
    user.pendTasks +=1
    user.save()
    return JsonResponse({'success': True, 'message': 'Task submitted successfully'}, status=200)

@csrf_exempt
def withdraw(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    amount = request.POST.get('amount')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Logout and try again'}, status=400)
    user = Token.objects.get(key=token_key).user
    if amount is None or float(amount) > user.balance:
        return JsonResponse({'error': True, 'message': 'Invalid data, try again'}, status=400)
    user.balance = user.balance - float(amount)
    user.save()
    PayOut.objects.create(user=user, amount=amount)
    return JsonResponse({'success': True}, status=200)

@csrf_exempt
def bankList(request):
    url = "https://api.paystack.co/bank"
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid auth token'}, status=400)
    headers = {"Authorization": f"Bearer {sk_token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data['status'] == True:
        return JsonResponse({'success': True, 'data': data['data']}, status=200)
    return JsonResponse({'error': True}, status=400)

@csrf_exempt
def bankResolve(request):
    url = "https://api.paystack.co/bank/resolve"
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    bank_code = request.POST.get('bank_code')
    account_number = request.POST.get('account_number')
    token_key = request.POST.get('token')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Invalid auth token'}, status=400)
    if bank_code is None or account_number is None or len(str(account_number)) < 10:
        return JsonResponse({'error': True, 'message': 'Invalid data parse'}, status=400)
    params = {"account_number": account_number, "bank_code": bank_code}
    headers = {"Authorization": f"Bearer {sk_token}"}
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if data['status'] == True:
        return JsonResponse({'success': True, 'data': data['data']}, status=200)
    return JsonResponse({'error': True}, status=400)

@csrf_exempt
def verification(request):
    if request.method != "POST":
        return JsonResponse({'error': True, 'message': 'Method not allowed'}, status=405)
    token_key = request.POST.get('token')
    govId = request.FILES.get('govId')
    studentId = request.FILES.get('studentId')
    if token_key is None or not Token.objects.filter(key=token_key).exists():
        return JsonResponse({'error': True, 'message': 'Logout and try again'}, status=400)
    if studentId is None or govId is None:
        return JsonResponse({'error': True, 'message': 'Invalid data, try again'}, status=400)
    user = Token.objects.get(key=token_key).user
    Document.objects.create(user=user, govID=govId, stuID=studentId)
    user.documentSubmitted = True
    user.save()
    return JsonResponse({'success': True, 'message': 'Document upload successfully'}, status=200)
