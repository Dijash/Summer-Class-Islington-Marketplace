from django.contrib import admin
from django.utils.html import format_html
from .models import SellerProfile, ProductRequest


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'business_name', 'pan_vat_number', 'status', 'is_verified', 'created_at')
    list_filter = ('status', 'is_verified', 'created_at')
    search_fields = ('shop_name', 'business_name', 'pan_vat_number', 'user__username', 'user__email')
    readonly_fields = ('pan_vat_front_preview', 'pan_vat_back_preview', 'created_at')
    actions = ['approve_applications', 'reject_applications']

    def pan_vat_front_preview(self, obj):
        if obj.pan_vat_front:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height: 220px; max-width: 340px; border-radius: 8px; border: 2px solid #cbd5e1; shadow: 0 4px 6px rgba(0,0,0,0.1);"/></a>', obj.pan_vat_front.url, obj.pan_vat_front.url)
        return "No document uploaded"
    pan_vat_front_preview.short_description = "PAN / VAT Card (Front Side)"

    def pan_vat_back_preview(self, obj):
        if obj.pan_vat_back:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height: 220px; max-width: 340px; border-radius: 8px; border: 2px solid #cbd5e1; shadow: 0 4px 6px rgba(0,0,0,0.1);"/></a>', obj.pan_vat_back.url, obj.pan_vat_back.url)
        return "No document uploaded"
    pan_vat_back_preview.short_description = "PAN / VAT Card (Back Side)"

    def save_model(self, request, obj, form, change):
        if obj.status == 'approved':
            obj.is_verified = True
        elif obj.status == 'rejected':
            obj.is_verified = False
        super().save_model(request, obj, form, change)

    @admin.action(description='Approve selected seller applications')
    def approve_applications(self, request, queryset):
        updated = queryset.update(status='approved', is_verified=True)
        self.message_user(request, f'{updated} seller application(s) approved successfully.')

    @admin.action(description='Reject selected seller applications')
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='rejected', is_verified=False)
        self.message_user(request, f'{updated} seller application(s) rejected.')


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

    color_names = [cn.strip() for cn in (pr.color_name or 'Default').split(',') if cn.strip()]
    color_codes = [cc.strip() for cc in (pr.color_code or '#000000').split(',') if cc.strip()]
    if not color_names:
        color_names = ['Default']

    for idx, cname in enumerate(color_names):
        code = color_codes[idx] if idx < len(color_codes) else '#000000'
        col = ProductColor.objects.create(
            product=product,
            color_name=cname,
            color_code=code,
            is_default=(idx == 0),
        )
        
        # Attach images for this color variant from ProductRequestImage
        color_imgs = pr.images.filter(color_index=idx).order_by('order')
        if color_imgs.exists():
            for req_img in color_imgs:
                ProductImage.objects.create(
                    color_variant=col,
                    image_url=req_img.image.url,
                    angle_label=req_img.angle_label,
                    order=req_img.order
                )
        elif idx == 0:
            # Fallback to single-set fields if pr.images is empty
            if pr.image:
                ProductImage.objects.create(color_variant=col, image_url=pr.image.url, angle_label='Front View', order=0)
            if pr.image2:
                ProductImage.objects.create(color_variant=col, image_url=pr.image2.url, angle_label='Side View', order=1)
            if pr.image3:
                ProductImage.objects.create(color_variant=col, image_url=pr.image3.url, angle_label='Back View', order=2)
            if pr.image4:
                ProductImage.objects.create(color_variant=col, image_url=pr.image4.url, angle_label='Detail View', order=3)



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
