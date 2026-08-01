from django.contrib import admin
from django.utils.text import slugify
from .models import SellerProfile, ProductRequest


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('shop_name', 'user__username')


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'brand_name', 'seller__shop_name')
    readonly_fields = ('seller', 'brand_name', 'title', 'category', 'mrp', 'price', 'description', 'image', 'quantity', 'created_at')

    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Approve selected requests & create products')
    def approve_requests(self, request, queryset):
        from product.models import Product, ProductColor, ProductImage
        approved = 0
        for pr in queryset.filter(status='pending'):
            # Create the actual product
            product = Product.objects.create(
                brand_name=pr.brand_name,
                title=pr.title,
                category=pr.category,
                mrp=pr.mrp,
                price=pr.price,
                description=pr.description,
                seller_name=pr.seller.shop_name,
                is_active=True,
            )
            # Create default color and image
            color = ProductColor.objects.create(product=product, color_name='Default', is_default=True)
            if pr.image:
                ProductImage.objects.create(color_variant=color, image_url=pr.image.url, angle_label='Front View')

            pr.product = product
            pr.status = 'approved'
            pr.save()
            approved += 1
        self.message_user(request, f'{approved} request(s) approved and product(s) created.')

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} request(s) rejected.')
