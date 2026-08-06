from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('404/', views.custom_404, name='custom_404'),
    path('500/', views.custom_500, name='custom_500'),
]

