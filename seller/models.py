from django.db import models
from django.contrib.auth.models import User
from core.models import Category


class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name = models.CharField(max_length=200)
    shop_description = models.TextField(blank=True, default='')
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

    class Meta:
        ordering = ['-created_at']
