from django.db import models

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
            return self.image_url
        return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1600&q=80"
