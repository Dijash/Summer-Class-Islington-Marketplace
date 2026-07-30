from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='customer_dashboard'),
    path('orders/', views.orders, name='customer_orders'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
