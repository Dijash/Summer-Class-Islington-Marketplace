from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model

User = get_user_model()

def login_view(request):
    if request.method in ['POST', 'GET'] and (request.method == 'POST' or 'email' in request.GET):
        email = request.POST.get('email') or request.GET.get('email') or 'admin@gmail.com'
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.first()
        if not user:
            user = User.objects.create_user(username='johndoe', email='john.doe@example.com', password='password123')
            
        auth_login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method in ['POST', 'GET'] and (request.method == 'POST' or 'email' in request.GET):
        email = request.POST.get('email') or request.GET.get('email') or 'newuser@marketplace.com'
        username = email.split('@')[0]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create_user(username=username, email=email, password='password123')
            
        auth_login(request, user)
        return redirect('home')

    return render(request, 'accounts/register.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def profile_view(request):
    return render(request, 'accounts/profile.html')
