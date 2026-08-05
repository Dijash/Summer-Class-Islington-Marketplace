import random
import time
from django.shortcuts import redirect
# pyrefly: ignore [missing-import]
from allauth.account.adapter import DefaultAccountAdapter
# pyrefly: ignore [missing-import]
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# pyrefly: ignore [missing-import]
from allauth.core.exceptions import ImmediateHttpResponse


class CustomAccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template=None, message_context=None, extra_tags="", message=None):
        if message_template in [
            'account/messages/logged_in.txt',
            'account/messages/logged_out.txt',
        ]:
            return
        super().add_message(
            request,
            level,
            message_template=message_template,
            message_context=message_context,
            extra_tags=extra_tags,
            message=message,
        )


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def add_message(self, request, level, message_template=None, message_context=None, extra_tags="", message=None):
        if message_template in [
            'socialaccount/messages/signed_in.txt',
            'socialaccount/messages/connected.txt',
        ]:
            return
        super().add_message(
            request,
            level,
            message_template=message_template,
            message_context=message_context,
            extra_tags=extra_tags,
            message=message,
        )

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)

        user_email = sociallogin.user.email or (sociallogin.account.extra_data.get('email') if sociallogin.account else '')
        if not user_email:
            return

        # 1. If social account is already linked to an existing user, bypass OTP and log in directly
        if sociallogin.is_existing:
            return

        # 2. If an account with this email already exists in the database, connect social account and bypass OTP
        from django.contrib.auth import get_user_model
        User = get_user_model()
        existing_user = User.objects.filter(email__iexact=user_email).first()
        if existing_user:
            if not sociallogin.is_existing:
                sociallogin.connect(request, existing_user)
            return

        # 3. If user has already verified OTP for this Google session, allow login
        if request.session.get('google_otp_verified') == user_email:
            return

        # 4. Only require OTP for NEW user registrations via Google
        otp_code = str(random.randint(100000, 999999))
        first_name = sociallogin.user.first_name or (sociallogin.account.extra_data.get('given_name') if sociallogin.account else '') or user_email.split('@')[0]

        request.session['google_signup_data'] = {
            'email': user_email,
            'first_name': first_name,
            'provider': sociallogin.account.provider,
        }
        request.session['google_sociallogin_state'] = sociallogin.serialize()
        request.session['google_signup_otp'] = otp_code
        request.session['google_otp_created_at'] = time.time()

        from accounts.views import send_otp_email
        send_otp_email(user_email, first_name, otp_code)

        raise ImmediateHttpResponse(redirect('verify_google_otp'))
