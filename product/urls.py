from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('detail/', views.product_detail, name='product_detail'),
    path('<int:pk>/', views.product_detail, name='product_detail_pk'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<int:product_id>/review/', views.submit_review, name='submit_review'),
]
