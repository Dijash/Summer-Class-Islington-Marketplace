from django.contrib import admin
from .models import Category, HeroBanner, BrandSpotlight, FeaturedCategory, ShopDrop

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('parent', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'button_text', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle', 'badge_text')
    ordering = ('order', '-created_at')


@admin.register(BrandSpotlight)
class BrandSpotlightAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'category_ref', 'discount_tag', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    filter_horizontal = ('parent_categories',)
    search_fields = ('name', 'discount_tag', 'logo_text')
    ordering = ('category', 'order', '-created_at')


@admin.register(FeaturedCategory)
class FeaturedCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_promo_card', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_promo_card', 'is_active', 'created_at')
    search_fields = ('title', 'brand_sub_title')
    ordering = ('order', '-created_at')


@admin.register(ShopDrop)
class ShopDropAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_tag', 'is_promo_card', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_promo_card', 'is_active', 'created_at')
    search_fields = ('title', 'offer_tag', 'promo_brand_text')
    ordering = ('order', '-created_at')
