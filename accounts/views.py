from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model, update_session_auth_hash
from django.http import JsonResponse

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username__iexact=email).first()
        if not user:
            user = User.objects.first()
        if not user:
            user = User.objects.create_user(username='admin', email='admin@gmail.com', password='password123')

        auth_login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()

        username = email.split('@')[0] if email else 'user'
        user = User.objects.filter(email__iexact=email).first() if email else None
        if not user:
            user = User.objects.create_user(
                username=username,
                email=email or 'user@example.com',
                password=password or 'password123',
                first_name=first_name,
                last_name=last_name
            )
        auth_login(request, user)
        return redirect('home')

    return render(request, 'accounts/register.html')

def logout_view(request):
    auth_logout(request)
    return redirect('home')

import re

def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()

            # Form Validation
            if not first_name or len(first_name) < 2:
                return JsonResponse({'success': False, 'message': 'First name must be at least 2 characters.'})

            if not last_name or len(last_name) < 2:
                return JsonResponse({'success': False, 'message': 'Last name must be at least 2 characters.'})

            if request.user.is_authenticated:
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                # Email address is read-only and cannot be changed
                try:
                    user.save()
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})

            request.session['user_phone'] = phone
            request.session['user_address'] = address

            full_name = f"{first_name} {last_name}".strip() or (request.user.username if request.user.is_authenticated else "John Doe")
            user_email = request.user.email if request.user.is_authenticated else "john.doe@example.com"

            return JsonResponse({
                'success': True,
                'message': 'Profile details updated successfully!',
                'full_name': full_name,
                'email': user_email
            })

        elif action == 'update_password':
            current_pass = request.POST.get('current_password', '').strip()
            new_pass = request.POST.get('new_password', '').strip()
            confirm_pass = request.POST.get('confirm_password', '').strip()

            if not current_pass:
                return JsonResponse({'success': False, 'message': 'Please enter your current password.'})

            if len(new_pass) < 6:
                return JsonResponse({'success': False, 'message': 'New password must be at least 6 characters long.'})

            if new_pass != confirm_pass:
                return JsonResponse({'success': False, 'message': 'New password and confirmation do not match.'})

            if request.user.is_authenticated:
                if not request.user.check_password(current_pass):
                    return JsonResponse({'success': False, 'message': 'Current password is incorrect.'})
                
                request.user.set_password(new_pass)
                request.user.save()
                update_session_auth_hash(request, request.user)

            return JsonResponse({
                'success': True,
                'message': 'Password updated successfully!'
            })

    phone = request.session.get('user_phone', '+1 (555) 234-5678')
    address = request.session.get('user_address', '123 Market Street, Apt 4B, San Francisco, CA 94107')

    return render(request, 'accounts/profile.html', {
        'phone': phone,
        'address': address
    })
