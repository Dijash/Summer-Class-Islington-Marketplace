from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.utils.html import json_script
import json
from datetime import timedelta
from .models import SellerProfile, ProductRequest, ProductRequestImage
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
    if not seller.is_verified and seller.status != 'approved':
        from django.contrib import messages
        messages.warning(request, 'You must submit your business details and be approved by an administrator to access the Seller Dashboard.')
        return redirect('profile')

    total_revenue = seller.total_revenue
    total_products = seller.total_products
    total_items_sold = seller.total_items_sold
    pending_requests = seller.pending_requests

    # Recent orders containing seller's products
    from customer.models import Order, OrderItem
    product_ids = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).exclude(product__is_active=False).exclude(product__isnull=True).values_list('product_id', flat=True)
    recent_orders = Order.objects.filter(
        items__product_id__in=product_ids
    ).distinct().select_related('user')[:5]

    # Recent requests
    recent_requests = ProductRequest.objects.filter(seller=seller).exclude(
        status='rejected'
    ).select_related('category')[:5]

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

    approved_count = ProductRequest.objects.filter(seller=seller, status='approved').exclude(product__is_active=False).exclude(product__isnull=True).count()
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
    ).exclude(product__is_active=False).exclude(product__isnull=True).values_list('product_id', flat=True)

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
    status_data = json.dumps({
        'approved': approved_count,
        'pending': pending_count,
        'rejected': rejected_count,
    })

    # Category breakdown
    category_data = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).exclude(product__is_active=False).exclude(product__isnull=True).values('category__name').annotate(count=Count('id')).order_by('-count')[:5]

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
        'category_data': json.dumps(list(category_data)),
    })


SIZES_CLOTHING = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '4XL']
SIZES_LINGERIE = ['30B', '32B', '32C', '34B', '34C', '36B', '36C', '38B', '38C']
SIZES_FOOTWEAR = ['UK 4', 'UK 5', 'UK 6', 'UK 7', 'UK 8', 'UK 9', 'UK 10', 'UK 11', 'UK 12']


COLOR_MAP = {
    'black': '#111111', 'ebony': '#111111', 'pitch': '#111111', 'jet': '#111111', 'midnight': '#0f172a',
    'white': '#ffffff', 'off white': '#fafaf9', 'off-white': '#fafaf9', 'cream': '#fef3c7', 'ivory': '#fffbeb', 'snow': '#f8fafc',
    'navy': '#0f172a', 'midnight navy': '#020617', 'dark blue': '#1e3a8a', 'blue': '#2563eb', 'royal blue': '#1d4ed8', 'cobalt': '#1e40af', 'sky blue': '#38bdf8', 'light blue': '#7dd3fc', 'baby blue': '#bae6fd', 'indigo': '#4f46e5', 'azure': '#0284c7',
    'red': '#dc2626', 'crimson': '#991b1b', 'ruby': '#b91c1c', 'scarlet': '#ef4444', 'cherry': '#c2410c', 'maroon': '#881337', 'burgundy': '#4c0519', 'wine': '#701a75', 'oxblood': '#450a0a',
    'pink': '#ec4899', 'rose': '#f43f5e', 'blush': '#f472b6', 'dusty rose': '#fb7185', 'fuchsia': '#d946ef', 'magenta': '#c026d3', 'peach': '#fdba74', 'coral': '#fb923c',
    'purple': '#8b5cf6', 'violet': '#7c3aed', 'plum': '#581c87', 'lavender': '#c084fc', 'lilac': '#e9d5ff', 'orchid': '#a855f7',
    'green': '#16a34a', 'dark green': '#14532d', 'forest green': '#166534', 'emerald': '#059669', 'olive': '#65a30d', 'army green': '#3f6212', 'khaki': '#84cc16', 'sage': '#86efac', 'mint': '#6ee7b7', 'seafoam': '#99f6e4',
    'yellow': '#eab308', 'mustard': '#ca8a04', 'gold': '#d97706', 'lemon': '#fde047', 'canary': '#facc15',
    'orange': '#ea580c', 'rust': '#c2410c', 'amber': '#f59e0b', 'terracotta': '#9a3412', 'copper': '#b45309',
    'brown': '#78350f', 'chocolate': '#451a03', 'coffee': '#78350f', 'tan': '#d97706', 'camel': '#b45309', 'chestnut': '#78350f', 'bronze': '#92400e',
    'beige': '#fef3c7', 'nude': '#fde68a', 'sand': '#fef08a', 'taupe': '#78716c', 'wheat': '#fef3c7',
    'grey': '#475569', 'gray': '#475569', 'dark grey': '#1e293b', 'dark gray': '#1e293b', 'charcoal': '#334155', 'slate': '#64748b', 'silver': '#cbd5e1', 'ash': '#94a3b8',
    'teal': '#0d9488', 'turquoise': '#14b8a6', 'cyan': '#06b6d4', 'aqua': '#22d3ee'
}


def get_color_hex_from_name(name):
    if not name:
        return '#000000'
    clean = name.strip().lower()
    if clean in COLOR_MAP:
        return COLOR_MAP[clean]
    for word in clean.split():
        if word in COLOR_MAP:
            return COLOR_MAP[word]
    h = sum(ord(c) for c in clean) % 360
    return f"hsl({h}, 45%, 45%)"


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

        color_names = request.POST.getlist('color_name')
        color_codes = request.POST.getlist('color_code')
        
        valid_colors = []
        for idx, cn in enumerate(color_names):
            name_str = cn.strip()
            if name_str:
                code_str = color_codes[idx].strip() if idx < len(color_codes) and color_codes[idx].strip() else get_color_hex_from_name(name_str)
                valid_colors.append((name_str, code_str))
        
        if not valid_colors:
            valid_colors = [('Default', '#000000')]

        color_name = ', '.join([c[0] for c in valid_colors])
        color_code = ', '.join([c[1] for c in valid_colors])
        sizes_list = request.POST.getlist('sizes')
        sizes = ','.join(sizes_list)
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        delivery_info = request.POST.get('delivery_info', '').strip()
        return_policy = request.POST.get('return_policy', '').strip()
        offers_text = request.POST.get('offers_text', '').strip()
        size_guidelines = request.POST.get('size_guidelines', '').strip()

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
                'colors_list': valid_colors,
                'sizes_clothing': SIZES_CLOTHING,
                'sizes_lingerie': SIZES_LINGERIE,
                'sizes_footwear': SIZES_FOOTWEAR,
                'form_data_sizes': sizes_list,
            })

        category = get_object_or_404(Category, pk=category_id)

        pr = ProductRequest.objects.create(
            seller=seller,
            brand_name=brand_name,
            title=title,
            category=category,
            mrp=float(mrp),
            price=float(price),
            description=description,
            image=image,
            quantity=int(quantity),
            color_name=color_name,
            color_code=color_code,
            sizes=sizes,
            image2=image2,
            image3=image3,
            image4=image4,
            delivery_info=delivery_info,
            return_policy=return_policy,
            offers_text=offers_text,
            size_guidelines=size_guidelines,
        )

        # Process per-color image uploads
        angles = [('Front View', 0), ('Side View', 1), ('Back View', 2), ('Detail View', 3)]
        for idx, (cname, ccode) in enumerate(valid_colors):
            for angle_name, angle_order in angles:
                img_key = f'color_{idx}_image_{angle_order}'
                img_file = request.FILES.get(img_key)
                if not img_file and idx == 0:
                    legacy_keys = {0: 'image', 1: 'image2', 2: 'image3', 3: 'image4'}
                    img_file = request.FILES.get(legacy_keys[angle_order])
                
                if img_file:
                    ProductRequestImage.objects.create(
                        product_request=pr,
                        color_index=idx,
                        color_name=cname,
                        image=img_file,
                        angle_label=angle_name,
                        order=angle_order,
                    )
                    if idx == 0:
                        if angle_order == 0: pr.image = img_file
                        elif angle_order == 1: pr.image2 = img_file
                        elif angle_order == 2: pr.image3 = img_file
                        elif angle_order == 3: pr.image4 = img_file

        pr.save()

        return redirect('seller_requests')

    return render(request, 'seller/add_product.html', {
        'seller': seller,
        'parent_categories': parent_categories,
        'sizes_clothing': SIZES_CLOTHING,
        'sizes_lingerie': SIZES_LINGERIE,
        'sizes_footwear': SIZES_FOOTWEAR,
        'form_data_sizes': [],
    })


@login_required(login_url='login')
def my_products(request):
    seller = get_or_create_seller(request.user)
    products = ProductRequest.objects.filter(
        seller=seller, status='approved'
    ).select_related('category', 'product').exclude(
        product__is_active=False
    ).exclude(product__isnull=True)
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
    ).exclude(product__is_active=False).exclude(product__isnull=True).values_list('product_id', flat=True)

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
