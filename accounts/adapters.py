from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def add_message(self, request, level, message_template=None, message_context=None, extra_tags="", message=None):
        # Suppress automatic login/logout banner notices to prevent cluttering checkout pages
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
        # Suppress automatic social sign-in banner notices
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
