from django.urls import path
from . import views

urlpatterns = [
    # Public Offers Page
    path('', views.public_offers_list, name='public_offers_list'),
    
    # Seller Offer Routes
    path('seller/', views.seller_offers_list, name='seller_offers_list'),
    path('seller/add/', views.seller_offer_create, name='seller_offer_create'),
    path('seller/<int:offer_id>/edit/', views.seller_offer_edit, name='seller_offer_edit'),
    path('seller/<int:offer_id>/delete/', views.seller_offer_delete, name='seller_offer_delete'),

    # Coupon AJAX Validation
    path('api/validate-coupon/', views.validate_coupon_api, name='validate_coupon_api'),

    # SuperAdmin Routes
    path('superadmin/login/', views.superadmin_login, name='superadmin_login'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/analytics/', views.superadmin_analytics, name='superadmin_analytics'),
    path('superadmin/sellers/', views.superadmin_sellers, name='superadmin_sellers'),
    path('superadmin/products/', views.superadmin_products, name='superadmin_products'),
    path('superadmin/products/reviews/', views.superadmin_product_reviews, name='superadmin_product_reviews'),
    path('superadmin/coupons/', views.superadmin_coupons, name='superadmin_coupons'),
    path('superadmin/promotions/', views.superadmin_promotions, name='superadmin_promotions'),
    path('superadmin/orders/', views.superadmin_orders, name='superadmin_orders'),
    path('superadmin/coupon/<int:coupon_id>/toggle/', views.superadmin_toggle_coupon, name='superadmin_toggle_coupon'),
    path('superadmin/coupon/<int:coupon_id>/delete/', views.superadmin_delete_coupon, name='superadmin_delete_coupon'),
    path('superadmin/offer/<int:offer_id>/delete/', views.superadmin_delete_offer, name='superadmin_delete_offer'),
    path('superadmin/offer/<int:offer_id>/toggle-status/', views.superadmin_toggle_offer_status, name='superadmin_toggle_offer_status'),
    path('superadmin/offer/<int:offer_id>/<str:action>/', views.superadmin_approve_offer, name='superadmin_approve_offer'),
    path('superadmin/product/add/', views.superadmin_add_product, name='superadmin_add_product'),
    path('superadmin/product/<int:product_id>/edit/', views.superadmin_edit_product, name='superadmin_edit_product'),
    path('superadmin/product/<int:product_id>/delete/', views.superadmin_delete_product, name='superadmin_delete_product'),
    path('superadmin/product/<int:product_id>/toggle-status/', views.superadmin_toggle_product_status, name='superadmin_toggle_product_status'),
    path('superadmin/product-request/<int:req_id>/<str:action>/', views.superadmin_approve_product_request, name='superadmin_approve_product_request'),
    path('superadmin/seller/<int:seller_id>/update-status/', views.superadmin_update_seller_status, name='superadmin_update_seller_status'),
    path('superadmin/seller/<int:seller_id>/<str:action>/', views.superadmin_approve_seller, name='superadmin_approve_seller'),
    path('superadmin/order/<int:order_id>/update-status/', views.superadmin_update_order_status, name='superadmin_update_order_status'),
]
