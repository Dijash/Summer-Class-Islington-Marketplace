from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Category or Brand name (e.g. Formal Menswear, Nike, Zara)")
    slug = models.SlugField(max_length=160, unique=True, blank=True, help_text="URL-friendly slug (auto-generated from name)")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category (e.g. Formal Menswear -> Polo, Calvin Klein, Hugo Boss)"
    )
    description = models.TextField(blank=True, help_text="Optional category description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Category thumbnail image")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this category from marketplace listings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_subcategories(self):
        return self.subcategories.filter(is_active=True)


class HeroBanner(models.Model):
    title = models.CharField(max_length=255, help_text="Main headline for the hero banner ad")
    subtitle = models.TextField(blank=True, help_text="Supporting description or promo offer text")
    badge_text = models.CharField(max_length=100, blank=True, help_text="Small pill badge text e.g., LIMITED TIME ONLY")
    image = models.ImageField(upload_to='hero_banners/', blank=True, null=True, help_text="High-resolution banner background image file")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional external image URL if no file is uploaded")
    button_text = models.CharField(max_length=50, default="Shop Collection")
    button_link = models.CharField(max_length=255, default="/product/")
    secondary_button_text = models.CharField(max_length=50, blank=True, default="Explore Deals")
    secondary_button_link = models.CharField(max_length=255, blank=True, default="/product/")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this ad from the hero carousel")
    order = models.PositiveIntegerField(default=0, help_text="Display order in carousel (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Hero Banner Ad"
        verbose_name_plural = "Hero Banner Ads"

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            if self.image_url.startswith('/static/'):
                from django.conf import settings
                prefix = settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL
                return self.image_url.replace('/static/', prefix)
            return self.image_url
        return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1600&q=80"


class BrandSpotlight(models.Model):
    CATEGORY_CHOICES = [
        ('women', "Women's Spotlight"),
        ('men', "Men's Spotlight"),
    ]

    name = models.CharField(max_length=150, help_text="Brand name (e.g. DAALI, Libas, Nike, Zara)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='women', help_text="Target category section (Women's or Men's)")
    category_ref = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brand_spotlights',
        help_text="Linked Category model for product filtering"
    )
    parent_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='featured_brands',
        help_text="Parent categories featuring this brand (e.g. Formal Menswear -> Calvin Klein, Polo)"
    )
    logo_text = models.CharField(max_length=150, blank=True, help_text="Custom logo text or markup to display on card")
    image = models.ImageField(upload_to='brand_spotlights/', blank=True, null=True, help_text="Brand card background image file")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="External image URL fallback")
    discount_tag = models.CharField(max_length=100, help_text="Promotional caption (e.g. MIN. 40% OFF, UNDER ₹999)")
    link = models.CharField(max_length=255, default="/product/", help_text="Destination link for card click")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this spotlight card")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers display first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Brand Spotlight"
        verbose_name_plural = "Brand Spotlights"

    def __str__(self):
        return f"{self.name} ({self.discount_tag})"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            if self.image_url.startswith('/static/'):
                from django.conf import settings
                prefix = settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL
                return self.image_url.replace('/static/', prefix)
            return self.image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"

    def get_destination_url(self):
        if self.category_ref:
            return f"/product/?category={self.category_ref.slug}"
        return self.link


class FeaturedCategory(models.Model):
    title = models.CharField(max_length=150, help_text="Category title (e.g. KURTAS & SUIT SETS, DRESSES, FORMAL MENSWEAR)")
    brand_sub_title = models.CharField(max_length=100, blank=True, help_text="Sub title/brand for promo card (e.g. WESTSIDE / MARKETPLACE)")
    category_ref = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_cards',
        help_text="Linked Category model for product filtering"
    )
    image = models.ImageField(upload_to='featured_categories/', blank=True, null=True, help_text="Category image file")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="External image URL fallback")
    is_promo_card = models.BooleanField(default=False, help_text="Check if this card is a solid promo banner (like Pink Sale card)")
    promo_bg_color = models.CharField(max_length=30, default="#d81b60", help_text="Background color hex for promo card (e.g. #d81b60)")
    link = models.CharField(max_length=255, default="/product/", help_text="Destination link for card click")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide card")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers display first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Featured Category Card"
        verbose_name_plural = "Featured Category Cards"

    def __str__(self):
        return f"{self.title} ({'Promo' if self.is_promo_card else 'Category Card'})"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            if self.image_url.startswith('/static/'):
                from django.conf import settings
                prefix = settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL
                return self.image_url.replace('/static/', prefix)
            return self.image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"

    def get_destination_url(self):
        if self.category_ref:
            return f"/product/?category={self.category_ref.slug}"
        return self.link


class ShopDrop(models.Model):
    title = models.CharField(max_length=150, help_text="Main title (e.g. WOMENSWEAR, HIS FOOTWEAR)")
    offer_tag = models.CharField(max_length=100, blank=True, help_text="Offer text (e.g. UP TO 70% OFF, MIN. 40% OFF)")
    category_ref = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shop_drop_items',
        help_text="Linked Category model for product filtering"
    )
    image = models.ImageField(upload_to='shop_drop/', blank=True, null=True, help_text="Category image file")
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="External image URL fallback")
    is_promo_card = models.BooleanField(default=False, help_text="Check if this card is a solid promo box (Pink SALE card)")
    promo_bg_color = models.CharField(max_length=30, default="#d81b60", help_text="Background color hex for promo card")
    promo_brand_text = models.CharField(max_length=100, default="MARKETPLACE", help_text="Sub title text for promo card (e.g. WESTSIDE / MARKETPLACE)")
    promo_caption = models.CharField(max_length=100, default="EXPRESS SHIPPING", help_text="Bottom caption for promo card")
    link = models.CharField(max_length=255, default="/product/")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Shop Drop Card"
        verbose_name_plural = "Shop Drop Cards"

    def __str__(self):
        return f"{self.title} ({self.offer_tag})"

    def get_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            if self.image_url.startswith('/static/'):
                from django.conf import settings
                prefix = settings.STATIC_URL if settings.STATIC_URL.startswith('/') else '/' + settings.STATIC_URL
                return self.image_url.replace('/static/', prefix)
            return self.image_url
        return "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=600&q=80"

    def get_destination_url(self):
        if self.category_ref:
            return f"/product/?category={self.category_ref.slug}"
        return self.link
