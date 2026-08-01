from django.urls import path
from . import views

urlpatterns = [
    path('', views.seller_dashboard, name='seller_dashboard'),
    path('analytics/', views.seller_analytics, name='seller_analytics'),
    path('add-product/', views.add_product, name='seller_add_product'),
    path('products/', views.my_products, name='seller_my_products'),
    path('requests/', views.seller_requests, name='seller_requests'),
    path('orders/', views.seller_orders, name='seller_orders'),
]
