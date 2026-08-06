from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from product.models import Product
from seller.models import SellerProfile

class Offer(models.Model):
    OFFER_TYPE_CHOICES = (
        ('percentage', 'Percentage Discount (%)'),
        ('fixed', 'Fixed Discount Amount'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage or Flat amount off")
    products = models.ManyToManyField(Product, related_name='offers', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_offers')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='offers', help_text="Null if created globally by Admin")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    admin_note = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.discount_value}{'%' if self.offer_type == 'percentage' else ' OFF'})"

    @property
    def is_valid(self):
        now = timezone.now()
        if self.status != 'approved':
            return False
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount (NPR)'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    )

    code = models.CharField(max_length=50, unique=True, help_text="e.g. SAVE20, SUMMER100")
    title = models.CharField(max_length=150, blank=True, default='')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum cart total required")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cap for percentage discount")
    usage_limit = models.PositiveIntegerField(default=100, help_text="Total number of times coupon can be used")
    times_used = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    valid_from = models.DateTimeField(default=timezone.now, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else ' NPR'}"

    @property
    def is_usable(self):
        if self.status != 'active':
            return False
        if self.times_used >= self.usage_limit:
            return False
        now = timezone.now()
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_to and self.valid_to < now:
            return False
        return True

    def calculate_discount(self, total_amount):
        try:
            total_val = float(total_amount)
            min_val = float(self.min_purchase_amount or 0)
            disc_val = float(self.discount_value or 0)
            max_val = float(self.max_discount_amount) if self.max_discount_amount is not None else None
        except (TypeError, ValueError):
            return 0.0

        if not self.is_usable or total_val < min_val:
            return 0.0

        if self.discount_type == 'percentage':
            discount = (total_val * disc_val) / 100.0
            if max_val is not None and discount > max_val:
                discount = max_val
            return round(discount, 2)
        else:
            return round(min(disc_val, total_val), 2)
