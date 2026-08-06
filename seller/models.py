from django.db import models
from django.contrib.auth.models import User
from core.models import Category


class SellerProfile(models.Model):
    STATUS_CHOICES = [
        ('unapplied', 'Not Applied'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True, default='')

    # Seller Verification & Document Fields
    business_name = models.CharField(max_length=255, blank=True, default='')
    pan_vat_number = models.CharField(max_length=50, blank=True, default='')
    pan_vat_front = models.ImageField(upload_to='seller_documents/', blank=True, null=True)
    pan_vat_back = models.ImageField(upload_to='seller_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unapplied')
    admin_note = models.TextField(blank=True, default='', help_text='Feedback or rejection reason from admin')
    submitted_at = models.DateTimeField(null=True, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name

    @property
    def total_revenue(self):
        from customer.models import Order, OrderItem
        product_ids = ProductRequest.objects.filter(
            seller=self, status='approved'
        ).exclude(product__is_active=False).exclude(product__isnull=True).values_list('product_id', flat=True)
        return float(
            OrderItem.objects.filter(
                product_id__in=product_ids, order__status='delivered'
            ).aggregate(total=models.Sum(models.F('price') * models.F('quantity')))['total'] or 0
        )

    @property
    def total_products(self):
        return ProductRequest.objects.filter(
            seller=self, status='approved'
        ).exclude(product__is_active=False).exclude(product__isnull=True).count()

    @property
    def total_items_sold(self):
        from customer.models import OrderItem
        product_ids = ProductRequest.objects.filter(
            seller=self, status='approved'
        ).exclude(product__is_active=False).exclude(product__isnull=True).values_list('product_id', flat=True)
        return OrderItem.objects.filter(
            product_id__in=product_ids, order__status='delivered'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def pending_requests(self):
        return ProductRequest.objects.filter(seller=self, status='pending').count()


class ProductRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='product_requests')
    product = models.OneToOneField('product.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='seller_request')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True, default='')

    brand_name = models.CharField(max_length=150)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)

    color_name = models.CharField(max_length=100, blank=True, default='Default')
    color_code = models.CharField(max_length=30, blank=True, default='#000000')
    sizes = models.CharField(max_length=255, blank=True, default='', help_text='Comma-separated sizes, e.g. S,M,L,XL')
    image = models.ImageField(upload_to='seller_products/', blank=True, null=True)
    image2 = models.ImageField(upload_to='seller_products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='seller_products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='seller_products/', blank=True, null=True)

    delivery_info = models.CharField(max_length=200, blank=True, default='Delivery by 3rd Aug')
    return_policy = models.CharField(max_length=200, blank=True, default='7 Days Return and Replacement available')
    offers_text = models.CharField(max_length=255, blank=True, default='Hurry! Get 5% Cashback. Offer ends tonight.')
    size_guidelines = models.TextField(blank=True, default='Please check size chart table to know the exact size to be ordered.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.seller.shop_name} [{self.status}]"

    def approve_and_sync_product(self):
        from product.models import Product, ProductColor, ProductImage, ProductSize
        self.status = 'approved'
        if not self.product:
            product = Product.objects.create(
                brand_name=self.brand_name,
                title=self.title,
                category=self.category,
                mrp=self.mrp,
                price=self.price,
                description=self.description,
                seller_name=self.seller.shop_name,
                delivery_info=self.delivery_info or 'Delivery by 3rd Aug',
                return_policy=self.return_policy or '7 Days Return and Replacement available',
                offers_text=self.offers_text or 'Hurry! Get 5% Cashback. Offer ends tonight.',
                size_guidelines=self.size_guidelines or 'Please check size chart table to know the exact size to be ordered.',
                stock=self.quantity,
                is_active=True,
            )
            color_names = [cn.strip() for cn in (self.color_name or 'Default').split(',') if cn.strip()]
            color_codes = [cc.strip() for cc in (self.color_code or '#000000').split(',') if cc.strip()]
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
                color_imgs = self.images.filter(color_index=idx).order_by('order')
                if color_imgs.exists():
                    for req_img in color_imgs:
                        ProductImage.objects.create(
                            color_variant=col,
                            image_url=req_img.image.url,
                            angle_label=req_img.angle_label,
                            order=req_img.order
                        )
                elif idx == 0:
                    if self.image:
                        ProductImage.objects.create(color_variant=col, image_url=self.image.url, angle_label='Front View', order=0)
                    if self.image2:
                        ProductImage.objects.create(color_variant=col, image_url=self.image2.url, angle_label='Side View', order=1)
                    if self.image3:
                        ProductImage.objects.create(color_variant=col, image_url=self.image3.url, angle_label='Back View', order=2)
                    if self.image4:
                        ProductImage.objects.create(color_variant=col, image_url=self.image4.url, angle_label='Detail View', order=3)

            if self.sizes:
                for size_label in [s.strip() for s in self.sizes.split(',') if s.strip()]:
                    ProductSize.objects.create(product=product, size_label=size_label, is_available=True)

            self.product = product
        else:
            p = self.product
            p.brand_name = self.brand_name
            p.title = self.title
            if self.category:
                p.category = self.category
            p.mrp = self.mrp
            p.price = self.price
            p.stock = self.quantity
            p.description = self.description
            p.delivery_info = self.delivery_info or p.delivery_info
            p.return_policy = self.return_policy or p.return_policy
            p.offers_text = self.offers_text or p.offers_text
            p.size_guidelines = self.size_guidelines or p.size_guidelines
            p.is_active = True
            p.save()
        self.save()
        return self.product

    class Meta:
        ordering = ['-created_at']


class ProductRequestImage(models.Model):
    product_request = models.ForeignKey(ProductRequest, on_delete=models.CASCADE, related_name='images')
    color_index = models.PositiveIntegerField(default=0)
    color_name = models.CharField(max_length=100, blank=True, default='')
    image = models.ImageField(upload_to='seller_products/')
    angle_label = models.CharField(max_length=100, default='Front View')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['color_index', 'order']

    def __str__(self):
        return f"{self.product_request.title} - {self.color_name} ({self.angle_label})"

