from django.contrib import admin
from .models import Offer, Coupon

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_type', 'discount_value', 'is_active', 'created_by', 'seller', 'created_at')
    list_filter = ('offer_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('products',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_purchase_amount', 'status', 'times_used', 'usage_limit', 'created_at')
    list_filter = ('discount_type', 'status', 'created_at')
    search_fields = ('code', 'title')
