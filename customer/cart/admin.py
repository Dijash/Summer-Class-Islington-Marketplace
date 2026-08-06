from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'size', 'color')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'item_count', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key')
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.get_total_count()
    item_count.short_description = 'Items'

    def total_price(self, obj):
        return f"₹{obj.get_total_price():.0f}"
    total_price.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'size', 'color', 'subtotal')
    list_filter = ('created_at',)
    search_fields = ('product__title',)

    def subtotal(self, obj):
        return f"₹{obj.get_subtotal():.0f}"
    subtotal.short_description = 'Subtotal'
