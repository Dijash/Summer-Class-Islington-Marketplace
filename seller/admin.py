from django.contrib import admin
from django.utils.text import slugify
from .models import SellerProfile, ProductRequest


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'rating', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('shop_name', 'user__username')


def create_product_from_request(pr):
    from product.models import Product, ProductColor, ProductImage, ProductSize

    product = Product.objects.create(
        brand_name=pr.brand_name,
        title=pr.title,
        category=pr.category,
        mrp=pr.mrp,
        price=pr.price,
        description=pr.description,
        seller_name=pr.seller.shop_name,
        delivery_info=pr.delivery_info or 'Delivery by 3rd Aug',
        return_policy=pr.return_policy or '7 Days Return and Replacement available',
        offers_text=pr.offers_text or 'Hurry! Get 5% Cashback. Offer ends tonight.',
        size_guidelines=pr.size_guidelines or 'Please check size chart table to know the exact size to be ordered.',
        is_active=True,
    )

    color = ProductColor.objects.create(
        product=product,
        color_name=pr.color_name or 'Default',
        color_code=pr.color_code or '#000000',
        is_default=True,
    )

    if pr.image:
        ProductImage.objects.create(color_variant=color, image_url=pr.image.url, angle_label='Front View', order=0)
    if pr.image2:
        ProductImage.objects.create(color_variant=color, image_url=pr.image2.url, angle_label='Side View', order=1)
    if pr.image3:
        ProductImage.objects.create(color_variant=color, image_url=pr.image3.url, angle_label='Back View', order=2)
    if pr.image4:
        ProductImage.objects.create(color_variant=color, image_url=pr.image4.url, angle_label='Detail View', order=3)

    if pr.sizes:
        for size_label in [s.strip() for s in pr.sizes.split(',') if s.strip()]:
            ProductSize.objects.create(product=product, size_label=size_label, is_available=True)

    return product


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'brand_name', 'seller__shop_name')
    readonly_fields = ('seller', 'created_at')

    actions = ['approve_requests', 'reject_requests', 'delete_requests']

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status == 'approved' and obj.product is None:
                product = create_product_from_request(obj)
                obj.product = product
            elif obj.status == 'rejected' and obj.product is not None:
                obj.product.is_active = False
                obj.product.save()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.product is not None:
            obj.product.delete()
        obj.delete()

    @admin.action(description='Approve selected requests & create products')
    def approve_requests(self, request, queryset):
        approved = 0
        for pr in queryset.exclude(status='approved'):
            if pr.product is None:
                product = create_product_from_request(pr)
                pr.product = product
            else:
                pr.product.is_active = True
                pr.product.save()
            pr.status = 'approved'
            pr.save()
            approved += 1
        self.message_user(request, f'{approved} request(s) approved and product(s) created.')

    @admin.action(description='Reject selected requests')
    def reject_requests(self, request, queryset):
        count = 0
        for pr in queryset.exclude(status='rejected'):
            if pr.product is not None:
                pr.product.is_active = False
                pr.product.save()
            pr.status = 'rejected'
            pr.save()
            count += 1
        self.message_user(request, f'{count} request(s) rejected.')

    @admin.action(description='Delete selected requests and associated products')
    def delete_requests(self, request, queryset):
        count = 0
        for pr in queryset:
            if pr.product is not None:
                pr.product.delete()
            pr.delete()
            count += 1
        self.message_user(request, f'{count} request(s) and associated product(s) deleted.')
