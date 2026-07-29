from django.urls import path
from . import views

urlpatterns = [
    path('', views.seller_dashboard, name='seller_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-product/', views.add_product, name='seller_add_product'),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('manage-products/', views.manage_products, name='seller_manage_products'),
]
