from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model, update_session_auth_hash
from django.http import JsonResponse

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            return render(request, 'accounts/login.html', {'error': 'Please enter both email and password.'})

        user = authenticate(request, username=email, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email__iexact=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is None:
            return render(request, 'accounts/login.html', {'error': 'Invalid email or password.'})

        auth_login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            return render(request, 'accounts/register.html', {'error': 'Please fill in all required fields.'})

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'accounts/register.html', {'error': 'An account with this email already exists.'})

        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
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
from .models import Profile

def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()

            if not first_name or len(first_name) < 2:
                return JsonResponse({'success': False, 'message': 'First name must be at least 2 characters.'})

            if not last_name or len(last_name) < 2:
                return JsonResponse({'success': False, 'message': 'Last name must be at least 2 characters.'})

            if request.user.is_authenticated:
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                try:
                    user.save()
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Database error: {str(e)}'})

                profile, _ = Profile.objects.get_or_create(user=user)
                profile.phone = phone
                profile.address = address
                profile.save()

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

        elif action == 'update_avatar':
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'You must be logged in.'})

            avatar_file = request.FILES.get('avatar')
            if not avatar_file:
                return JsonResponse({'success': False, 'message': 'No image file provided.'})

            if not avatar_file.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': 'Please select a valid image file.'})

            if avatar_file.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'message': 'Image must be under 5MB.'})

            profile, _ = Profile.objects.get_or_create(user=request.user)
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = avatar_file
            profile.save()

            return JsonResponse({
                'success': True,
                'message': 'Profile photo updated successfully!',
                'avatar_url': profile.avatar.url
            })

    profile = None
    wishlist_count = 0
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        from customer.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'wishlist_count': wishlist_count,
    })
