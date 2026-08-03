from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialAccount
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        instance.profile.save()


@receiver(user_logged_in)
@receiver(user_signed_up)
@receiver(pre_social_login)
def sync_social_profile_picture(sender, request=None, user=None, sociallogin=None, **kwargs):
    target_user = user or (sociallogin.user if sociallogin else None)
    if not target_user or not target_user.pk:
        return
    
    if not hasattr(target_user, 'profile'):
        Profile.objects.create(user=target_user)
        
    try:
        social_acc = SocialAccount.objects.filter(user=target_user).first()
        if not social_acc and sociallogin:
            social_acc = sociallogin.account

        if social_acc and social_acc.extra_data:
            picture_url = social_acc.extra_data.get('picture') or social_acc.get_avatar_url()
            if picture_url and target_user.profile.avatar_url != picture_url:
                target_user.profile.avatar_url = picture_url
                target_user.profile.save()
    except Exception:
        pass
