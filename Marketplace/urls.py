from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('cart/', include('customer.cart.urls')),
    path('', include('core.urls')),
    path('offers/', include('offers.urls')),
    path('customer/', include('customer.urls')),
    path('product/', include('product.urls')),
    path('seller/', include('seller.urls')),
]

handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# Serve static & media files unconditionally in development mode
import os

def serve_static(request, path):
    root = settings.STATIC_ROOT if (settings.STATIC_ROOT and os.path.exists(os.path.join(settings.STATIC_ROOT, path))) else settings.STATICFILES_DIRS[0]
    return serve(request, path, document_root=root)

urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve_static),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]



