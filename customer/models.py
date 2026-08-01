from django.db import models
from django.contrib.auth.models import User
from product.models import Product


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user or self.session_key} - {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, blank=True, default='')
    shipping_address = models.TextField(blank=True, default='')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"

    @property
    def status_badge_class(self):
        mapping = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'shipped': 'badge-primary',
            'in_transit': 'badge-warning',
            'delivered': 'badge-success',
            'cancelled': 'badge-danger',
            'returned': 'badge-secondary',
        }
        return mapping.get(self.status, 'badge-secondary')

    @property
    def status_icon(self):
        mapping = {
            'pending': 'fa-clock',
            'processing': 'fa-cog',
            'shipped': 'fa-box',
            'in_transit': 'fa-truck',
            'delivered': 'fa-check',
            'cancelled': 'fa-xmark',
            'returned': 'fa-rotate-left',
        }
        return mapping.get(self.status, 'fa-circle')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=255)
    product_image = models.URLField(max_length=500, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_title} x{self.quantity}"

    @property
    def item_total(self):
        return self.price * self.quantity
