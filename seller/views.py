from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import SellerProfile, ProductRequest
from core.models import Category


def get_or_create_seller(user):
    profile, _ = SellerProfile.objects.get_or_create(
        user=user,
        defaults={'shop_name': f"{user.first_name or user.username}'s Store"}
    )
    return profile


@login_required(login_url='login')
def seller_dashboard(request):
    seller = get_or_create_seller(request.user)

    total_revenue = seller.total_revenue
    total_products = seller.total_products
    total_items_sold = seller.total_items_sold
    pending_requests = seller.pending_requests

    # Recent requests
    recent_requests = ProductRequest.objects.filter(seller=seller)[:5]

    # Recent orders containing seller's products
    from customer.models import Order, OrderItem
    product_ids = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).values_list('product_id', flat=True)
    recent_orders = Order.objects.filter(
        items__product_id__in=product_ids
    ).distinct()[:5]

    return render(request, 'seller/dashboard.html', {
        'seller': seller,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_items_sold': total_items_sold,
        'pending_requests': pending_requests,
        'recent_requests': recent_requests,
        'recent_orders': recent_orders,
    })


@login_required(login_url='login')
def seller_analytics(request):
    seller = get_or_create_seller(request.user)

    approved_count = ProductRequest.objects.filter(seller=seller, status='approved').count()
    pending_count = ProductRequest.objects.filter(seller=seller, status='pending').count()
    rejected_count = ProductRequest.objects.filter(seller=seller, status='rejected').count()
    total_products = seller.total_products
    total_items_sold = seller.total_items_sold
    total_revenue = seller.total_revenue

    # Monthly revenue data for chart (last 6 months)
    months = []
    revenue_data = []
    orders_data = []
    from customer.models import OrderItem, Order
    product_ids = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).values_list('product_id', flat=True)

    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30 * i)
        month_label = month_date.strftime('%b')
        months.append(month_label)

        month_revenue = OrderItem.objects.filter(
            product_id__in=product_ids,
            order__status='delivered',
            order__created_at__month=month_date.month,
            order__created_at__year=month_date.year
        ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        revenue_data.append(float(month_revenue))

        month_orders = Order.objects.filter(
            items__product_id__in=product_ids,
            created_at__month=month_date.month,
            created_at__year=month_date.year
        ).distinct().count()
        orders_data.append(month_orders)

    # Status breakdown for pie chart
    status_data = {
        'approved': approved_count,
        'pending': pending_count,
        'rejected': rejected_count,
    }

    # Category breakdown
    category_data = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).values('category__name').annotate(count=Count('id')).order_by('-count')[:5]

    return render(request, 'seller/analytics.html', {
        'seller': seller,
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_items_sold': total_items_sold,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'months': months,
        'revenue_data': revenue_data,
        'orders_data': orders_data,
        'status_data': status_data,
        'category_data': list(category_data),
    })


@login_required(login_url='login')
def add_product(request):
    seller = get_or_create_seller(request.user)
    parent_categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('subcategories')

    if request.method == 'POST':
        brand_name = request.POST.get('brand_name', '').strip()
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category')
        mrp = request.POST.get('mrp', '').strip()
        price = request.POST.get('price', '').strip()
        description = request.POST.get('description', '').strip()
        quantity = request.POST.get('quantity', '1').strip()
        image = request.FILES.get('image')

        errors = []
        if not brand_name:
            errors.append('Brand name is required.')
        if not title:
            errors.append('Product title is required.')
        if not category_id:
            errors.append('Category is required.')
        if not mrp or float(mrp) <= 0:
            errors.append('Valid MRP is required.')
        if not price or float(price) <= 0:
            errors.append('Valid price is required.')
        if float(price) > float(mrp):
            errors.append('Price cannot be greater than MRP.')
        if image and not image.content_type.startswith('image/'):
            errors.append('Please upload a valid image file.')
        if image and image.size > 5 * 1024 * 1024:
            errors.append('Image must be under 5MB.')

        if errors:
            return render(request, 'seller/add_product.html', {
                'seller': seller,
                'parent_categories': parent_categories,
                'errors': errors,
                'form_data': request.POST,
            })

        category = get_object_or_404(Category, pk=category_id)

        ProductRequest.objects.create(
            seller=seller,
            brand_name=brand_name,
            title=title,
            category=category,
            mrp=float(mrp),
            price=float(price),
            description=description,
            image=image,
            quantity=int(quantity),
        )

        return redirect('seller_requests')

    return render(request, 'seller/add_product.html', {
        'seller': seller,
        'parent_categories': parent_categories,
    })


@login_required(login_url='login')
def my_products(request):
    seller = get_or_create_seller(request.user)
    products = ProductRequest.objects.filter(seller=seller, status='approved').select_related('category', 'product')
    return render(request, 'seller/my_products.html', {
        'seller': seller,
        'products': products,
    })


@login_required(login_url='login')
def seller_requests(request):
    seller = get_or_create_seller(request.user)
    status_filter = request.GET.get('status', '')

    requests_qs = ProductRequest.objects.filter(seller=seller).select_related('category')
    if status_filter in ['pending', 'approved', 'rejected']:
        requests_qs = requests_qs.filter(status=status_filter)

    status_counts = ProductRequest.objects.filter(seller=seller).values('status').annotate(count=Count('id'))
    counts = {item['status']: item['count'] for item in status_counts}
    counts['all'] = sum(counts.values())

    return render(request, 'seller/requests.html', {
        'seller': seller,
        'requests': requests_qs,
        'status_counts': counts,
        'active_filter': status_filter,
    })


@login_required(login_url='login')
def seller_orders(request):
    seller = get_or_create_seller(request.user)
    status_filter = request.GET.get('status', '')

    product_ids = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).values_list('product_id', flat=True)

    from customer.models import Order, OrderItem
    orders_qs = Order.objects.filter(
        items__product_id__in=product_ids
    ).distinct().select_related('user')

    if status_filter in ['pending', 'processing', 'shipped', 'in_transit', 'delivered', 'cancelled', 'returned']:
        orders_qs = orders_qs.filter(status=status_filter)

    # Status counts
    all_orders = Order.objects.filter(items__product_id__in=product_ids).distinct()
    status_counts = all_orders.values('status').annotate(count=Count('id'))
    counts = {item['status']: item['count'] for item in status_counts}
    counts['all'] = all_orders.count()

    # Total revenue from delivered orders
    delivered_revenue = OrderItem.objects.filter(
        product_id__in=product_ids, order__status='delivered'
    ).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

    return render(request, 'seller/orders.html', {
        'seller': seller,
        'orders': orders_qs,
        'status_counts': counts,
        'active_filter': status_filter,
        'delivered_revenue': delivered_revenue,
    })
