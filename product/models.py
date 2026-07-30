from django.db import models
from django.utils.text import slugify
from core.models import Category

class Product(models.Model):
    brand_name = models.CharField(max_length=150, help_text="Brand name e.g., Jockey, Nike, Calvin Klein")
    title = models.CharField(max_length=255, help_text="Full product title")
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original MRP price")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discounted selling price")
    rating = models.FloatField(default=4.5, help_text="Star rating out of 5.0")
    ratings_count = models.PositiveIntegerField(default=12, help_text="Total ratings count")
    reviews_count = models.PositiveIntegerField(default=3, help_text="Total reviews count")
    description = models.TextField(blank=True, help_text="Detailed product description")
    size_guidelines = models.TextField(blank=True, default="Please check size chart table to know the exact size to be ordered.")
    offers_text = models.CharField(max_length=255, blank=True, default="Hurry! Get 5% Cashback. Offer ends tonight.")
    seller_name = models.CharField(max_length=200, default="1 PAGE INDUSTRIES LIMITED")
    delivery_info = models.CharField(max_length=200, default="Delivery by 3rd Aug")
    return_policy = models.CharField(max_length=200, default="7 Days Return and Replacement available")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand_name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand_name}-{self.title}")
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.mrp and self.price and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0

    @property
    def default_color(self):
        return self.colors.filter(is_default=True).first() or self.colors.first()

    @property
    def primary_image(self):
        def_color = self.default_color
        if def_color and def_color.images.exists():
            return def_color.images.first().image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color_name = models.CharField(max_length=100, help_text="Color name e.g. Orchid Smoke, Midnight Navy")
    color_code = models.CharField(max_length=30, default="#000000", help_text="Hex code e.g. #D4829C")
    swatch_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} - {self.color_name}"


class ProductImage(models.Model):
    color_variant = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    angle_label = models.CharField(max_length=100, default="Front View")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.color_variant.product.title} [{self.color_variant.color_name}] ({self.angle_label})"


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size_label = models.CharField(max_length=50, help_text="Size e.g. 32B, 34C, S, M, L, 42")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.title} - {self.size_label}"
