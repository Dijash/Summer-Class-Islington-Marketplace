from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from core.models import Category

class Product(models.Model):
    brand_name = models.CharField(max_length=150, help_text="Brand name e.g., Jockey, Nike, Calvin Klein")
    title = models.CharField(max_length=255, help_text="Full product title")
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original MRP price")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discounted selling price")
    rating = models.FloatField(default=2.0, help_text="Average star rating out of 5.0")
    ratings_count = models.PositiveIntegerField(default=0, help_text="Total ratings count")
    reviews_count = models.PositiveIntegerField(default=0, help_text="Total reviews count")
    description = models.TextField(blank=True, help_text="Detailed product description")
    size_guidelines = models.TextField(blank=True, default="Please check size chart table to know the exact size to be ordered.")
    offers_text = models.CharField(max_length=255, blank=True, default="Hurry! Get 5% Cashback. Offer ends tonight.")
    seller_name = models.CharField(max_length=200, default="1 PAGE INDUSTRIES LIMITED")
    delivery_info = models.CharField(max_length=200, default="Delivery by 3rd Aug")
    return_policy = models.CharField(max_length=200, default="7 Days Return and Replacement available")
    stock = models.PositiveIntegerField(default=10, help_text="Available stock quantity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_in_stock(self):
        return self.is_active and self.stock > 0

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
    def active_offer(self):
        try:
            from django.utils import timezone
            now = timezone.now()
            active_offers = self.offers.filter(is_active=True, start_date__lte=now)
            valid_offers = [o for o in active_offers if not o.end_date or o.end_date >= now]
            if valid_offers:
                return max(valid_offers, key=lambda o: float(o.discount_value))
        except Exception:
            pass
        return None

    @property
    def discount_percentage(self):
        offer = self.active_offer
        if offer:
            if offer.offer_type == 'percentage':
                return int(float(offer.discount_value))
            elif offer.offer_type == 'fixed':
                base = float(self.mrp) if (self.mrp and self.mrp > 0) else float(self.price)
                if base and base > 0:
                    return int((float(offer.discount_value) / base) * 100)
        
        if self.mrp and self.price and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp) * 100)
        return 0

    @property
    def discount_label(self):
        offer = self.active_offer
        if offer:
            if offer.offer_type == 'percentage':
                val = int(float(offer.discount_value)) if float(offer.discount_value).is_integer() else float(offer.discount_value)
                return f"{val}% off"
            elif offer.offer_type == 'fixed':
                val = int(float(offer.discount_value)) if float(offer.discount_value).is_integer() else float(offer.discount_value)
                return f"NPR {val} off"
        
        pct = self.discount_percentage
        if pct > 0:
            return f"{pct}% off"
        return ""

    @property
    def computed_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else (self.rating or 2.0)
        return self.rating or 2.0

    @property
    def computed_reviews_count(self):
        count = self.reviews.count()
        if count > 0:
            return count
        return self.reviews_count or 0

    @property
    def rating_breakdown(self):
        reviews = self.reviews.all()
        total = reviews.count()
        if total == 0:
            empty_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
            return {'counts': empty_counts, 'percentages': empty_counts, 'total': 0}
        counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
        percentages = {k: round((v / total) * 100) for k, v in counts.items()}
        return {'counts': counts, 'percentages': percentages, 'total': total}

    @property
    def default_color(self):
        return self.colors.filter(is_default=True).first() or self.colors.first()

    @property
    def primary_image(self):
        def_color = self.default_color
        if def_color and def_color.images.exists():
            return def_color.images.first().image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=2)
    title = models.CharField(max_length=200, blank=True, default='')
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_product_rating()

    def _update_product_rating(self):
        product = self.product
        reviews = product.reviews.all()
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            product.rating = round(avg, 1) if avg else 2.0
            product.ratings_count = reviews.count()
            product.reviews_count = reviews.count()
        else:
            product.rating = 2.0
            product.ratings_count = 0
            product.reviews_count = 0
        product.save(update_fields=['rating', 'ratings_count', 'reviews_count'])


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
