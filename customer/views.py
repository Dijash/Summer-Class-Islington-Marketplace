from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count, Q
from product.models import Product
from .models import Wishlist, Order

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
    from cart.models import Cart
    
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.get_total_count()
    else:
        session_key = get_session_key(request)
        wishlist_count = Wishlist.objects.filter(session_key=session_key).count()
        cart = Cart.objects.filter(session_key=session_key).first()
        if cart:
            cart_count = cart.get_total_count()

    phone = request.session.get('user_phone', '+1 (555) 234-5678')
    address = request.session.get('user_address', '123 Market Street, Apt 4B, San Francisco, CA 94107')

    return render(request, 'customer/dashboard.html', {
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
        'phone': phone,
        'address': address
    })

def orders(request):
    if not request.user.is_authenticated:
        return render(request, 'customer/orders.html', {'orders': [], 'status_counts': {}})

    status_filter = request.GET.get('status', '').strip()

    orders_qs = Order.objects.filter(user=request.user).prefetch_related('items', 'items__product')

    if status_filter and status_filter in ['pending', 'processing', 'shipped', 'in_transit', 'delivered', 'cancelled', 'returned']:
        orders_qs = orders_qs.filter(status=status_filter)

    orders_list = orders_qs[:50]

    status_counts = Order.objects.filter(user=request.user).values('status').annotate(count=Count('id'))
    counts = {item['status']: item['count'] for item in status_counts}
    counts['all'] = sum(counts.values())

    return render(request, 'customer/orders.html', {
        'orders': orders_list,
        'status_counts': counts,
        'active_filter': status_filter,
    })
