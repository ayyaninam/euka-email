from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from .models import Email as Email_model
from .models import TestEmail

# Create your views here.
def home(request):
    return render(request, 'base/home.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('base:home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('base:home')
        else:
            return redirect('base:login')

    return render(request, 'base/login.html')

def logout(request):
    auth_logout(request)
    return redirect('base:home')

def view_email(request):
    # change this to filter with users
    all_emails = Email_model.objects.all()
    context = {
        'all_emails':all_emails
    }
    return render(request, 'base/view_email.html', context)

def add_email(request):
    if request.method == "POST":
        email_host_user = request.POST.get('email_host_user')
        email_host_password = ' '.join(request.POST.get('email_host_password').split()) 
        email_host_port = request.POST.get('email_host_port')
        email_host_smtp_host = request.POST.get('email_host_smtp_host')
        email_host_use_tls = True if request.POST.get('email_host_use_tls') == "on" else False
        try:
            Email_model.objects.get(email_host_user = email_host_user)
            # raise validation error of already existence
        except:
            new_email = Email_model.objects.create(
                email_host_user = email_host_user,
                email_host_password = email_host_password,
                email_host_port = email_host_port,
                email_host_smtp_host = email_host_smtp_host,
                email_host_use_tls = email_host_use_tls
            )
            
        return redirect('base:add_email')
    return render(request, 'base/add_email.html')

def add_campaign(request):
    return render(request, 'base/add_campaign.html')

def generate_fake_email(request):
    for i in range(1000):
        TestEmail.objects.create(
            email = f"{i}@gmail.com"
        )
    return HttpResponse('Success!')