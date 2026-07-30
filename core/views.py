from django.shortcuts import render
from .models import HeroBanner

def index(request):
    hero_banners = HeroBanner.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/index.html', {
        'hero_banners': hero_banners
    })

def contact(request):
    return render(request, 'core/contact.html')
