from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from product.models import Product
from customer.models import Order, OrderItem
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


def _calc_totals(cart):
    cart_items = cart.items.select_related('product').all() if cart else []
    subtotal = float(sum(i.get_subtotal() for i in cart_items))
    shipping = 0 if subtotal > 1000 or subtotal == 0 else 99
    tax = round(subtotal * 0.05, 2)
    grand_total = subtotal + shipping + tax
    total_count = sum(i.quantity for i in cart_items)
    return {
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'count': total_count,
    }


def cart_view(request):
    cart, _ = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []
    totals = _calc_totals(cart)

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'tax': totals['tax'],
        'grand_total': totals['grand_total'],
        'item_count': totals['count'],
    })


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
            return JsonResponse({'success': False, 'login_required': True, 'message': 'Please log in to add items to your cart'}, status=403)
        return redirect('login')

    product = get_object_or_404(Product, pk=product_id)
    cart, _ = get_or_create_cart(request)
    if not cart:
        return JsonResponse({'success': False, 'message': 'Unable to create cart'}, status=400)

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

    totals = _calc_totals(cart)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({
            'success': True,
            'message': f"Added '{product.title}' to cart!",
            'count': totals['count'],
            'total_price': totals['subtotal'],
        })

    return redirect('cart')


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart = cart_item.cart
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

    totals = _calc_totals(cart)

    return JsonResponse({
        'success': True,
        'item_qty': cart_item.quantity if cart_item else 0,
        'item_subtotal': float(cart_item.get_subtotal()) if cart_item else 0,
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'tax': totals['tax'],
        'grand_total': totals['grand_total'],
        'count': totals['count'],
    })


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart = cart_item.cart
    cart_item.delete()

    totals = _calc_totals(cart)

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart',
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'tax': totals['tax'],
        'grand_total': totals['grand_total'],
        'count': totals['count'],
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
                'size': i.size or '',
                'color': i.color or '',
                'image': i.product.primary_image,
                'subtotal': float(i.get_subtotal()),
            })
    return JsonResponse({
        'count': cart.get_total_count() if cart else 0,
        'subtotal': float(cart.get_total_price()) if cart else 0,
        'items': items,
    })


def checkout_view(request):
    cart, _ = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []
    totals = _calc_totals(cart)

    user_profile = None
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': totals['subtotal'],
        'shipping': totals['shipping'],
        'tax': totals['tax'],
        'grand_total': totals['grand_total'],
        'item_count': totals['count'],
        'user_profile': user_profile,
    })


def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to place an order.')
        return redirect('login')

    cart, _ = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []

    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    street = request.POST.get('street_address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    zip_code = request.POST.get('zip_code', '').strip()
    shipping_method = request.POST.get('shipping_method', '')
    payment_type = request.POST.get('payment_type', '')

    if not all([first_name, last_name, email, phone, street, city, state, zip_code]):
        messages.error(request, 'Please fill in all required shipping fields.')
        return redirect('checkout')

    if not shipping_method:
        messages.error(request, 'Please select a shipping method.')
        return redirect('checkout')

    if not payment_type:
        messages.error(request, 'Please select a payment method.')
        return redirect('checkout')

    shipping_address = f"{first_name} {last_name}\n{street}\n{city}, {state} {zip_code}\nPhone: {phone}\nEmail: {email}"

    totals = _calc_totals(cart)
    shipping_cost = 0 if shipping_method == 'standard' else 12.99
    grand_total = totals['subtotal'] + shipping_cost + totals['tax']

    order = Order.objects.create(
        user=request.user,
        order_number=f"ORD-{Order.objects.count() + 10001}",
        status='pending',
        shipping_address=shipping_address,
        total_amount=grand_total,
    )

    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_title=cart_item.product.title,
            product_image=cart_item.product.primary_image,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )

    cart_items.delete()
    cart.delete()

    messages.success(request, f'Order #{order.order_number} placed successfully!')
    return redirect('customer_orders')
