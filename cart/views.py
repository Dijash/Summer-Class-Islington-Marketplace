from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from product.models import Product
from .models import Cart, CartItem

def get_or_create_cart(request):
    if not hasattr(request, 'session') or request.session is None:
        session_key = None
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            if session_key:
                cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if cart:
                cart.user = request.user
                cart.save()
            else:
                cart = Cart.objects.create(user=request.user)
    else:
        if not session_key:
            return None, None
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)

    return cart, session_key

def cart_view(request):
    cart, _ = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []
    
    subtotal = sum(item.get_subtotal() for item in cart_items)
    shipping = 0 if subtotal > 1000 or subtotal == 0 else 99
    tax = round(subtotal * 0.05, 2)
    grand_total = subtotal + shipping + tax

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'item_count': sum(item.quantity for item in cart_items)
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity') or request.GET.get('quantity') or 1)
    size = request.POST.get('size') or request.GET.get('size') or ''
    color = request.POST.get('color') or request.GET.get('color') or ''

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        color=color,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    total_count = cart.get_total_count()
    total_price = cart.get_total_price()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': True,
            'message': f"Added '{product.title}' to cart!",
            'count': total_count,
            'total_price': float(total_price)
        })

    return redirect('cart')

def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    action = request.POST.get('action') or request.GET.get('action')
    quantity = request.POST.get('quantity') or request.GET.get('quantity')

    if quantity is not None:
        new_qty = int(quantity)
        if new_qty > 0:
            cart_item.quantity = new_qty
            cart_item.save()
        else:
            cart_item.delete()
            cart_item = None
    elif action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            cart_item = None

    cart = cart_item.cart if cart_item else get_or_create_cart(request)[0]
    cart_items = cart.items.all() if cart else []
    subtotal = float(sum(i.get_subtotal() for i in cart_items))
    shipping = 0 if subtotal > 1000 or subtotal == 0 else 99
    tax = round(subtotal * 0.05, 2)
    grand_total = subtotal + shipping + tax
    total_count = sum(i.quantity for i in cart_items)

    return JsonResponse({
        'success': True,
        'item_qty': cart_item.quantity if cart_item else 0,
        'item_subtotal': float(cart_item.get_subtotal()) if cart_item else 0,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'count': total_count
    })

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart = cart_item.cart
    cart_item.delete()

    cart_items = cart.items.all()
    subtotal = float(sum(i.get_subtotal() for i in cart_items))
    shipping = 0 if subtotal > 1000 or subtotal == 0 else 99
    tax = round(subtotal * 0.05, 2)
    grand_total = subtotal + shipping + tax
    total_count = sum(i.quantity for i in cart_items)

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'count': total_count
    })

def cart_summary_api(request):
    cart, _ = get_or_create_cart(request)
    items = []
    if cart:
        for i in cart.items.select_related('product').all():
            items.append({
                'id': i.id,
                'title': i.product.title,
                'slug': i.product.slug,
                'price': float(i.product.price),
                'quantity': i.quantity,
                'image': i.product.primary_image,
                'subtotal': float(i.get_subtotal())
            })
    return JsonResponse({
        'count': cart.get_total_count() if cart else 0,
        'subtotal': float(cart.get_total_price()) if cart else 0,
        'items': items
    })

def checkout_view(request):
    return render(request, 'cart/checkout.html')

