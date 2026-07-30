from django.contrib import admin
from .models import Product, ProductColor, ProductImage, ProductSize

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand_name', 'category', 'price', 'mrp', 'rating', 'seller_name', 'is_active', 'created_at')
    list_editable = ('price', 'is_active')
    list_filter = ('category', 'brand_name', 'is_active', 'created_at')
    search_fields = ('title', 'brand_name', 'description')
    prepopulated_fields = {'slug': ('brand_name', 'title')}
    inlines = [ProductColorInline, ProductSizeInline]

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'color_name', 'color_code', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('product__title', 'color_name')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('color_variant', 'angle_label', 'order')

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size_label', 'is_available')
