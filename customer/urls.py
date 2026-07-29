from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='customer_dashboard'),
    path('orders/', views.orders, name='customer_orders'),
]
