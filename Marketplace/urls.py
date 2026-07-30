from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('', include('core.urls')),
    path('customer/', include('customer.urls')),
    path('product/', include('product.urls')),
    path('seller/', include('seller.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
