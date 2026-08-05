from django.shortcuts import render
from .models import HeroBanner, BrandSpotlight, FeaturedCategory, ShopDrop

def index(request):
    hero_banners = HeroBanner.objects.filter(is_active=True).order_by('order')
    women_brand_spotlights = BrandSpotlight.objects.filter(is_active=True, category='women').order_by('order')
    men_brand_spotlights = BrandSpotlight.objects.filter(is_active=True, category='men').order_by('order')
    featured_categories = FeaturedCategory.objects.filter(is_active=True).order_by('order')
    shop_drops = ShopDrop.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/index.html', {
        'hero_banners': hero_banners,
        'women_brand_spotlights': women_brand_spotlights,
        'men_brand_spotlights': men_brand_spotlights,
        'featured_categories': featured_categories,
        'shop_drops': shop_drops,
    })

def contact(request):
    return render(request, 'core/contact.html')

def custom_404(request, exception=None):
    return render(request, 'error_page/404.html', status=404)

import traceback

def custom_500(request):
    traceback.print_exc()
    return render(request, 'error_page/500.html', status=500)

