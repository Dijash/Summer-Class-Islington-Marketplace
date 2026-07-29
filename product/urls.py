from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('detail/', views.product_detail, name='product_detail'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
]
