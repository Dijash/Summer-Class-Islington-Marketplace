from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from product.models import Product
from .models import Wishlist

def get_session_key(request):
    if not hasattr(request, 'session') or request.session is None:
        return 'anonymous_session'
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def wishlist_view(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    else:
        session_key = get_session_key(request)
        wishlist_items = Wishlist.objects.filter(session_key=session_key).select_related('product')

    products = [item.product for item in wishlist_items]

    return render(request, 'customer/wishlist.html', {
        'wishlist_items': wishlist_items,
        'products': products,
        'count': len(products)
    })

def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.user.is_authenticated:
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            wishlist_item.delete()
            added = False
        else:
            added = True
        total_count = Wishlist.objects.filter(user=request.user).count()
    else:
        session_key = get_session_key(request)
        wishlist_item, created = Wishlist.objects.get_or_create(session_key=session_key, product=product)
        if not created:
            wishlist_item.delete()
            added = False
        else:
            added = True
        total_count = Wishlist.objects.filter(session_key=session_key).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'added': added,
            'count': total_count,
            'message': 'Added to Wishlist' if added else 'Removed from Wishlist'
        })

    return redirect('wishlist')

def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, product=product).delete()
    else:
        session_key = get_session_key(request)
        Wishlist.objects.filter(session_key=session_key, product=product).delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('wishlist')

def dashboard(request):
    return render(request, 'customer/dashboard.html')

def orders(request):
    return render(request, 'customer/orders.html')
