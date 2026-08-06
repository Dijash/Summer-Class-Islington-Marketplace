from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/summary/', views.cart_summary_api, name='cart_summary_api'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('khalti/verify/', views.khalti_verify, name='khalti_verify'),
    path('khalti/gateway/', views.khalti_gateway_sandbox, name='khalti_gateway_sandbox'),
]
