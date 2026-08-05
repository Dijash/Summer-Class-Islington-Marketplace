from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model, update_session_auth_hash
from django.http import JsonResponse
# pyrefly: ignore [missing-import]
from allauth.socialaccount.models import SocialLogin
# pyrefly: ignore [missing-import]
from allauth.socialaccount.helpers import complete_social_login

User = get_user_model()

def is_ajax_request(request):
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    )

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

import random
import time
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives

def send_otp_email(user_email, first_name, otp_code):
    subject = f"{otp_code} is your Islington MarketPlace verification code"
    
    plain_message = (
        f"Hello {first_name},\n\n"
        f"Your Islington MarketPlace verification code is: {otp_code}\n\n"
        f"This code will expire in 10 minutes. If you did not request this verification, please ignore this email.\n\n"
        f"Best regards,\nIslington MarketPlace Security Team"
    )

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Islington MarketPlace Verification Code</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 40px 10px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 540px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); border: 1px solid #e2e8f0;">
                        
                        <!-- Header Banner -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 30px; text-align: center; border-bottom: 3px solid #3b82f6;">
                                <h1 style="color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: 1.5px; margin: 0; text-transform: uppercase;">ISLINGTON MARKETPLACE</h1>
                                <p style="color: #94a3b8; font-size: 13px; margin: 6px 0 0 0; font-weight: 500; letter-spacing: 0.5px;">Account Verification & Security</p>
                            </td>
                        </tr>

                        <!-- Body Content -->
                        <tr>
                            <td style="padding: 36px 32px 28px 32px;">
                                <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin-top: 0; margin-bottom: 12px;">Hello {first_name}</h2>
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin-top: 0; margin-bottom: 24px;">
                                    Thank you for choosing <strong>Islington MarketPlace</strong>. Use the 6-digit verification code below to authorize your account access:
                                </p>

                                <!-- OTP Code Box -->
                                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 28px;">
                                    <tr>
                                        <td align="center" style="background: #0f172a; border-radius: 14px; padding: 24px 16px; border: 1px solid #334155;">
                                            <span style="font-family: 'Courier New', Courier, monospace; font-size: 38px; font-weight: 800; letter-spacing: 10px; color: #38bdf8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.25); display: inline-block;">
                                                {otp_code}
                                            </span>
                                            <div style="margin-top: 10px; color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                                Expires in 10 minutes
                                            </div>
                                        </td>
                                    </tr>
                                </table>

                                <!-- Notice Box -->
                                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; border-left: 4px solid #0f172a; border-radius: 6px; margin-bottom: 24px;">
                                    <tr>
                                        <td style="padding: 14px 16px;">
                                            <p style="color: #334155; font-size: 13px; line-height: 1.5; margin: 0;">
                                                <strong>Security Note:</strong> Never share this verification code with anyone. Our support team will never ask for your code over the phone or email.
                                            </p>
                                        </td>
                                    </tr>
                                </table>

                                <p style="color: #64748b; font-size: 13px; line-height: 1.5; margin: 0;">
                                    If you didn't request this code, you can safely ignore this email — your account remains completely secure.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="color: #94a3b8; font-size: 12px; margin: 0; line-height: 1.5;">
                                    © 2026 Islington MarketPlace. All rights reserved.<br>
                                    This is an automated security notification. Please do not reply directly to this email.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    print("\n" + "="*65)
    print(f"  🔑 [OTP CODE GENERATED] User: {user_email} | OTP: {otp_code}")
    print("="*65 + "\n")

    email_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    sender_email = getattr(settings, 'EMAIL_HOST_USER', 'utsavbhattarai29@gmail.com')
    from_email = f"Islington MarketPlace <{sender_email}>"

    sent = False
    if email_pass:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=[user_email],
                headers={'Reply-To': sender_email}
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            print(f"[MAIL SUCCESS] Premium OTP email sent via SMTP to {user_email}")
            return True
        except Exception as e:
            print(f"[SMTP FAIL] Could not send via SMTP: {e}")

    try:
        connection = get_connection('django.core.mail.backends.console.EmailBackend')
        msg = EmailMultiAlternatives(subject, plain_message, from_email, [user_email], connection=connection)
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        print(f"[MAIL CONSOLE] OTP printed to console for {user_email}")
        return True
    except Exception as e:
        print(f"[CONSOLE FAIL] Failed fallback email send: {e}")
        return False


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        account_type = request.POST.get('account_type', 'buyer').strip()
        business_name = request.POST.get('business_name', '').strip()

        if not email or not password or not first_name or not last_name:
            return render(request, 'accounts/register.html', {'error': 'Please fill in all required fields.'})

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'accounts/register.html', {'error': 'An account with this email already exists.'})

        otp_code = str(random.randint(100000, 999999))

        request.session['signup_data'] = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'account_type': account_type,
            'business_name': business_name,
        }
        request.session['signup_otp'] = otp_code
        request.session['otp_created_at'] = time.time()

        send_otp_email(email, first_name, otp_code)

        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def verify_otp_view(request):
    signup_data = request.session.get('signup_data')
    signup_otp = request.session.get('signup_otp')
    otp_created_at = request.session.get('otp_created_at', 0)

    if not signup_data or not signup_otp:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    user_email = signup_data.get('email', '')

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        if not otp_input:
            d1 = request.POST.get('otp_1', '')
            d2 = request.POST.get('otp_2', '')
            d3 = request.POST.get('otp_3', '')
            d4 = request.POST.get('otp_4', '')
            d5 = request.POST.get('otp_5', '')
            d6 = request.POST.get('otp_6', '')
            otp_input = f"{d1}{d2}{d3}{d4}{d5}{d6}".strip()

        if time.time() - otp_created_at > 600:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'}, status=400)
            return render(request, 'accounts/verify_otp.html', {
                'email': user_email,
                'error': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'
            })

        if otp_input == str(signup_otp):
            email = signup_data['email']
            first_name = signup_data['first_name']
            last_name = signup_data['last_name']
            password = signup_data['password']
            account_type = signup_data.get('account_type', 'buyer')
            business_name = signup_data.get('business_name', '')

            if User.objects.filter(email__iexact=email).exists():
                if is_ajax_request(request):
                    return JsonResponse({'success': False, 'message': 'Account with this email already exists.'}, status=400)
                messages.error(request, 'Account with this email already exists.')
                return redirect('login')

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

            if account_type == 'seller':
                try:
                    from seller.models import SellerProfile
                    shop_name = business_name or f"{first_name}'s Shop"
                    SellerProfile.objects.get_or_create(user=user, defaults={'shop_name': shop_name})
                except Exception:
                    pass

            auth_login(request, user)

            request.session.pop('signup_data', None)
            request.session.pop('signup_otp', None)
            request.session.pop('otp_created_at', None)

            if is_ajax_request(request):
                return JsonResponse({
                    'success': True,
                    'message': 'Account successfully created!',
                    'title': 'Account Successfully Created!',
                    'subtitle': f'Welcome to Islington MarketPlace, {first_name}! Your account has been verified and is ready to explore.',
                    'redirect_url': '/'
                })

            messages.success(request, 'Email verified successfully! Welcome to MarketPlace.')
            return redirect('home')
        else:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'Invalid verification code. Please check your email and try again.'}, status=400)
            return render(request, 'accounts/verify_otp.html', {
                'email': user_email,
                'error': 'Invalid verification code. Please check your email and try again.'
            })

    return render(request, 'accounts/verify_otp.html', {'email': user_email})


def resend_otp_view(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Session expired. Please register again.'}, status=400)
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    email = signup_data.get('email', '')
    first_name = signup_data.get('first_name', '')
    otp_code = str(random.randint(100000, 999999))

    request.session['signup_otp'] = otp_code
    request.session['otp_created_at'] = time.time()

    success = send_otp_email(email, first_name, otp_code)

    if is_ajax_request(request):
        if success:
            return JsonResponse({'success': True, 'message': f'A new verification code has been sent to {email}.'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send verification email. Please try again.'}, status=500)

    messages.success(request, f'A new verification code has been sent to {email}.')
    return redirect('verify_otp')

def verify_google_otp_view(request):
    google_data = request.session.get('google_signup_data')
    google_otp = request.session.get('google_signup_otp')
    otp_created_at = request.session.get('google_otp_created_at', 0)
    sociallogin_state = request.session.get('google_sociallogin_state')

    if not google_data or not google_otp:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Google sign-in session expired. Please try signing in again.'}, status=400)
        messages.error(request, 'Google sign-in session expired. Please try signing in with Google again.')
        return redirect('login')

    user_email = google_data.get('email', '')

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        if not otp_input:
            d1 = request.POST.get('otp_1', '')
            d2 = request.POST.get('otp_2', '')
            d3 = request.POST.get('otp_3', '')
            d4 = request.POST.get('otp_4', '')
            d5 = request.POST.get('otp_5', '')
            d6 = request.POST.get('otp_6', '')
            otp_input = f"{d1}{d2}{d3}{d4}{d5}{d6}".strip()

        if time.time() - otp_created_at > 600:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'}, status=400)
            return render(request, 'accounts/verify_google_otp.html', {
                'email': user_email,
                'error': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'
            })

        if otp_input == str(google_otp):
            request.session['google_otp_verified'] = user_email

            request.session.pop('google_signup_data', None)
            request.session.pop('google_signup_otp', None)
            request.session.pop('google_otp_created_at', None)
            request.session.pop('google_sociallogin_state', None)

            # Fallback to direct Django authentication if deserialization fails
            from django.contrib.auth import get_user_model, login as auth_login
            User = get_user_model()
            user = User.objects.filter(email__iexact=user_email).first()
            if not user:
                first_name = google_data.get('first_name', '')
                username = user_email.split('@')[0]
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user = User.objects.create_user(
                    username=username,
                    email=user_email,
                    first_name=first_name
                )

            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            if is_ajax_request(request):
                first_name = user.first_name or user_email.split('@')[0]
                return JsonResponse({
                    'success': True,
                    'message': 'Google email verified successfully!',
                    'title': 'Account Successfully Verified!',
                    'subtitle': f'Welcome to Islington MarketPlace, {first_name}! Your Google account has been verified and you are now logged in.',
                    'redirect_url': '/'
                })

            messages.success(request, 'Google email verified successfully! Welcome to MarketPlace.')
            return redirect('/')
        else:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'Invalid verification code. Please check your email and try again.'}, status=400)
            return render(request, 'accounts/verify_google_otp.html', {
                'email': user_email,
                'error': 'Invalid verification code. Please check your email and try again.'
            })

    return render(request, 'accounts/verify_google_otp.html', {'email': user_email})


def resend_google_otp_view(request):
    google_data = request.session.get('google_signup_data')
    if not google_data:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Session expired. Please try signing in again.'}, status=400)
        messages.error(request, 'Session expired. Please try signing in again.')
        return redirect('login')

    email = google_data.get('email', '')
    first_name = google_data.get('first_name', '')
    otp_code = str(random.randint(100000, 999999))

    request.session['google_signup_otp'] = otp_code
    request.session['google_otp_created_at'] = time.time()

    success = send_otp_email(email, first_name, otp_code)

    if is_ajax_request(request):
        if success:
            return JsonResponse({'success': True, 'message': f'A new verification code has been sent to {email}.'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send verification email. Please try again.'}, status=500)

    messages.success(request, f'A new verification code has been sent to {email}.')
    return redirect('verify_google_otp')


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

        elif action == 'apply_seller':
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'message': 'You must be logged in to apply as a seller.'})

            business_name = request.POST.get('business_name', '').strip()
            pan_vat_number = request.POST.get('pan_vat_number', '').strip()
            pan_vat_front = request.FILES.get('pan_vat_front')
            pan_vat_back = request.FILES.get('pan_vat_back')

            if not business_name or len(business_name) < 2:
                return JsonResponse({'success': False, 'message': 'Please enter a valid Business / Shop Name.'})

            if not pan_vat_number or len(pan_vat_number) < 3:
                return JsonResponse({'success': False, 'message': 'Please enter a valid PAN or VAT registration number.'})

            from seller.models import SellerProfile
            from django.utils import timezone

            seller_profile = SellerProfile.objects.filter(user=request.user).first()

            # For new application, both document files are required
            if not seller_profile or (not seller_profile.pan_vat_front and not pan_vat_front):
                if not pan_vat_front:
                    return JsonResponse({'success': False, 'message': 'Please upload the front side of your PAN / VAT card.'})

            if not seller_profile or (not seller_profile.pan_vat_back and not pan_vat_back):
                if not pan_vat_back:
                    return JsonResponse({'success': False, 'message': 'Please upload the back side of your PAN / VAT card.'})

            if pan_vat_front and not pan_vat_front.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': 'Front side document must be a valid image file.'})

            if pan_vat_back and not pan_vat_back.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': 'Back side document must be a valid image file.'})

            if not seller_profile:
                seller_profile = SellerProfile.objects.create(
                    user=request.user,
                    shop_name=business_name,
                    business_name=business_name,
                    pan_vat_number=pan_vat_number,
                    status='pending',
                    submitted_at=timezone.now()
                )
            else:
                seller_profile.shop_name = business_name
                seller_profile.business_name = business_name
                seller_profile.pan_vat_number = pan_vat_number
                seller_profile.status = 'pending'
                seller_profile.submitted_at = timezone.now()

            if pan_vat_front:
                seller_profile.pan_vat_front = pan_vat_front
            if pan_vat_back:
                seller_profile.pan_vat_back = pan_vat_back

            seller_profile.save()

            return JsonResponse({
                'success': True,
                'message': 'Your seller application has been submitted successfully! An administrator will review your details shortly.'
            })

    profile = None
    seller_profile = None
    wishlist_count = 0
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        from seller.models import SellerProfile
        seller_profile = SellerProfile.objects.filter(user=request.user).first()
        from customer.models import Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'seller_profile': seller_profile,
        'wishlist_count': wishlist_count,
    })


def send_reset_otp_email(user_email, first_name, otp_code):
    subject = f"{otp_code} is your Islington MarketPlace password reset code"
    
    plain_message = (
        f"Hello {first_name},\n\n"
        f"Your Islington MarketPlace password reset code is: {otp_code}\n\n"
        f"This code will expire in 10 minutes. If you did not request a password reset, please ignore this email.\n\n"
        f"Best regards,\nIslington MarketPlace Security Team"
    )

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Islington MarketPlace Password Reset</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 40px 10px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 540px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); border: 1px solid #e2e8f0;">
                        <tr>
                            <td style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 32px 30px; text-align: center; border-bottom: 3px solid #3b82f6;">
                                <h1 style="color: #ffffff; font-size: 22px; font-weight: 800; letter-spacing: 1.5px; margin: 0; text-transform: uppercase;">ISLINGTON MARKETPLACE</h1>
                                <p style="color: #94a3b8; font-size: 13px; margin: 6px 0 0 0; font-weight: 500; letter-spacing: 0.5px;">Password Reset & Security</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 36px 32px 28px 32px;">
                                <h2 style="color: #0f172a; font-size: 20px; font-weight: 700; margin-top: 0; margin-bottom: 12px;">Hello {first_name}</h2>
                                <p style="color: #475569; font-size: 15px; line-height: 1.6; margin-top: 0; margin-bottom: 24px;">
                                    We received a request to reset your password for your <strong>Islington MarketPlace</strong> account. Use the 6-digit code below to set a new password:
                                </p>

                                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 28px;">
                                    <tr>
                                        <td align="center" style="background: #0f172a; border-radius: 14px; padding: 24px 16px; border: 1px solid #334155;">
                                            <span style="font-family: 'Courier New', Courier, monospace; font-size: 38px; font-weight: 800; letter-spacing: 10px; color: #38bdf8; text-shadow: 0 0 12px rgba(56, 189, 248, 0.25); display: inline-block;">
                                                {otp_code}
                                            </span>
                                            <div style="margin-top: 10px; color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                                Expires in 10 minutes
                                            </div>
                                        </td>
                                    </tr>
                                </table>

                                <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; border-left: 4px solid #0f172a; border-radius: 6px; margin-bottom: 24px;">
                                    <tr>
                                        <td style="padding: 14px 16px;">
                                            <p style="color: #334155; font-size: 13px; line-height: 1.5; margin: 0;">
                                                <strong>Security Warning:</strong> If you did not request this password reset, please ignore this email. Your password will remain unchanged.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color: #f8fafc; padding: 24px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="color: #94a3b8; font-size: 12px; margin: 0; line-height: 1.5;">
                                    © 2026 Islington MarketPlace. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    print("\n" + "="*65)
    print(f"  🔑 [RESET OTP GENERATED] User: {user_email} | OTP: {otp_code}")
    print("="*65 + "\n")

    email_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    sender_email = getattr(settings, 'EMAIL_HOST_USER', 'utsavbhattarai29@gmail.com')
    from_email = f"Islington MarketPlace <{sender_email}>"

    if email_pass:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=[user_email],
                headers={'Reply-To': sender_email}
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            print(f"[MAIL SUCCESS] Password Reset OTP email sent via SMTP to {user_email}")
            return True
        except Exception as e:
            print(f"[SMTP FAIL] Could not send via SMTP: {e}")

    try:
        connection = get_connection('django.core.mail.backends.console.EmailBackend')
        msg = EmailMultiAlternatives(subject, plain_message, from_email, [user_email], connection=connection)
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        print(f"[MAIL CONSOLE] Reset OTP printed to console for {user_email}")
        return True
    except Exception as e:
        print(f"[CONSOLE FAIL] Failed fallback email send: {e}")
        return False


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'Please enter your account email address.'}, status=400)
            return render(request, 'accounts/forgot_password.html', {'error': 'Please enter your account email address.'})

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'No registered account found with this email address.'}, status=404)
            return render(request, 'accounts/forgot_password.html', {'error': 'No registered account found with this email address.', 'email': email})

        otp_code = str(random.randint(100000, 999999))
        first_name = user.first_name or user.username

        request.session['reset_user_email'] = email
        request.session['reset_otp'] = otp_code
        request.session['reset_otp_created_at'] = time.time()
        request.session['reset_otp_verified'] = False

        send_reset_otp_email(email, first_name, otp_code)

        if is_ajax_request(request):
            return JsonResponse({
                'success': True,
                'message': f'Verification code sent to {email}.',
                'redirect_url': '/accounts/verify-reset-otp/'
            })

        messages.success(request, f'A password reset verification code has been sent to {email}.')
        return redirect('verify_reset_otp')

    return render(request, 'accounts/forgot_password.html')


def verify_reset_otp_view(request):
    reset_email = request.session.get('reset_user_email')
    reset_otp = request.session.get('reset_otp')
    otp_created_at = request.session.get('reset_otp_created_at', 0)

    if not reset_email or not reset_otp:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Password reset session expired. Please try again.'}, status=400)
        messages.error(request, 'Password reset session expired. Please enter your email again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()
        if not otp_input:
            d1 = request.POST.get('otp_1', '')
            d2 = request.POST.get('otp_2', '')
            d3 = request.POST.get('otp_3', '')
            d4 = request.POST.get('otp_4', '')
            d5 = request.POST.get('otp_5', '')
            d6 = request.POST.get('otp_6', '')
            otp_input = f"{d1}{d2}{d3}{d4}{d5}{d6}".strip()

        if time.time() - otp_created_at > 600:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'}, status=400)
            return render(request, 'accounts/verify_reset_otp.html', {
                'email': reset_email,
                'error': 'OTP code has expired. Please click "Resend Code" to receive a new OTP.'
            })

        if otp_input == str(reset_otp):
            request.session['reset_otp_verified'] = True

            if is_ajax_request(request):
                return JsonResponse({
                    'success': True,
                    'message': 'Code verified successfully! You can now set your new password.',
                    'redirect_url': '/accounts/reset-password/'
                })

            messages.success(request, 'Code verified successfully! You can now set your new password.')
            return redirect('reset_password')
        else:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'Invalid verification code. Please check your email and try again.'}, status=400)
            return render(request, 'accounts/verify_reset_otp.html', {
                'email': reset_email,
                'error': 'Invalid verification code. Please check your email and try again.'
            })

    return render(request, 'accounts/verify_reset_otp.html', {'email': reset_email})


def resend_reset_otp_view(request):
    reset_email = request.session.get('reset_user_email')
    if not reset_email:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Session expired. Please try again.'}, status=400)
        messages.error(request, 'Session expired. Please try again.')
        return redirect('forgot_password')

    user = User.objects.filter(email__iexact=reset_email).first()
    first_name = user.first_name if user else reset_email.split('@')[0]
    otp_code = str(random.randint(100000, 999999))

    request.session['reset_otp'] = otp_code
    request.session['reset_otp_created_at'] = time.time()
    request.session['reset_otp_verified'] = False

    success = send_reset_otp_email(reset_email, first_name, otp_code)

    if is_ajax_request(request):
        if success:
            return JsonResponse({'success': True, 'message': f'A new reset code has been sent to {reset_email}.'})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send reset code email. Please try again.'}, status=500)

    messages.success(request, f'A new reset code has been sent to {reset_email}.')
    return redirect('verify_reset_otp')


def reset_password_view(request):
    reset_email = request.session.get('reset_user_email')
    is_verified = request.session.get('reset_otp_verified', False)

    if not reset_email or not is_verified:
        if is_ajax_request(request):
            return JsonResponse({'success': False, 'message': 'Unauthorized or session expired. Please verify your OTP code first.'}, status=403)
        messages.error(request, 'Please verify your reset code first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if len(new_password) < 6:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'New password must be at least 6 characters long.'}, status=400)
            return render(request, 'accounts/reset_password.html', {'error': 'New password must be at least 6 characters long.'})

        if new_password != confirm_password:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'New password and confirmation do not match.'}, status=400)
            return render(request, 'accounts/reset_password.html', {'error': 'New password and confirmation do not match.'})

        user = User.objects.filter(email__iexact=reset_email).first()
        if not user:
            if is_ajax_request(request):
                return JsonResponse({'success': False, 'message': 'User account not found.'}, status=404)
            return redirect('login')

        user.set_password(new_password)
        user.save()

        # Clear reset session state
        request.session.pop('reset_user_email', None)
        request.session.pop('reset_otp', None)
        request.session.pop('reset_otp_created_at', None)
        request.session.pop('reset_otp_verified', None)

        if is_ajax_request(request):
            return JsonResponse({
                'success': True,
                'message': 'Password reset successfully!',
                'title': 'Password Successfully Reset!',
                'subtitle': 'Your password has been updated. You can now log in to your account with your new password.',
                'redirect_url': '/accounts/login/'
            })

        messages.success(request, 'Password reset successfully! You can now log in with your new password.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html', {'email': reset_email})
