import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from .models import Offer, Coupon
from .forms import SellerOfferForm, AdminOfferForm, CouponForm
from product.models import Product
from seller.models import SellerProfile
try:
    from customer.models import Order
except ImportError:
    Order = None
from core.models import Category

def is_super_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

# ==============================================================================
# PUBLIC OFFERS VIEW
# ==============================================================================
def public_offers_list(request):
    now = timezone.now()
    active_offers = Offer.objects.filter(is_active=True).prefetch_related('products')
    active_coupons = Coupon.objects.filter(status='active')
    
    # Products attached to any active offer
    discounted_products = Product.objects.filter(
        is_active=True,
        offers__is_active=True
    ).distinct()[:16]

    return render(request, 'offers/public_offers.html', {
        'active_offers': active_offers,
        'active_coupons': active_coupons,
        'discounted_products': discounted_products,
    })


# ==============================================================================
# SELLER OFFER MANAGEMENT (Sellers can ONLY select their accepted products)
# ==============================================================================
@login_required
def seller_offers_list(request):
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, "Access restricted. You must be a registered seller.")
        return redirect('home')

    offers = Offer.objects.filter(seller=seller_profile).order_by('-created_at')
    return render(request, 'offers/seller_offers.html', {
        'offers': offers,
        'seller_profile': seller_profile
    })


@login_required
def seller_offer_create(request):
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, "Access restricted. You must be a registered seller.")
        return redirect('home')

    if request.method == 'POST':
        form = SellerOfferForm(request.POST, seller_profile=seller_profile)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.created_by = request.user
            offer.seller = seller_profile
            offer.status = 'pending'
            offer.is_active = False
            offer.save()
            form.save_m2m()
            messages.success(request, f"Offer '{offer.title}' submitted for admin review and approval!")
            return redirect('seller_offers_list')
    else:
        form = SellerOfferForm(seller_profile=seller_profile)

    return render(request, 'offers/seller_offer_form.html', {
        'form': form,
        'seller_profile': seller_profile
    })


@login_required
def seller_offer_edit(request, offer_id):
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, "Access restricted. You must be a registered seller.")
        return redirect('home')

    offer = get_object_or_404(Offer, pk=offer_id, seller=seller_profile)
    if request.method == 'POST':
        form = SellerOfferForm(request.POST, instance=offer, seller_profile=seller_profile)
        if form.is_valid():
            updated_offer = form.save(commit=False)
            updated_offer.status = 'pending'
            updated_offer.is_active = False
            updated_offer.save()
            form.save_m2m()
            messages.success(request, f"Offer '{updated_offer.title}' updates submitted for admin review and approval!")
            return redirect('seller_offers_list')
    else:
        form = SellerOfferForm(instance=offer, seller_profile=seller_profile)

    return render(request, 'offers/seller_offer_form.html', {
        'form': form,
        'offer': offer,
        'is_edit': True,
        'seller_profile': seller_profile
    })


@login_required
def seller_offer_delete(request, offer_id):
    try:
        seller_profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return redirect('home')

    offer = get_object_or_404(Offer, pk=offer_id, seller=seller_profile)
    offer.delete()
    messages.success(request, "Offer deleted successfully.")
    return redirect('seller_offers_list')


# ==============================================================================
# COUPON VALIDATION API
# ==============================================================================
def validate_coupon_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    
    code = request.POST.get('code', '').strip()
    try:
        cart_total = float(request.POST.get('cart_total', 0))
    except (ValueError, TypeError):
        cart_total = 0.0

    if not code:
        return JsonResponse({'success': False, 'message': 'Please enter a coupon code.'})

    coupon = Coupon.objects.filter(code__iexact=code).first()
    if not coupon:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})

    if not coupon.is_usable:
        return JsonResponse({'success': False, 'message': 'This coupon is either paused, expired, or has reached its max usage limit.'})

    if cart_total < float(coupon.min_purchase_amount):
        return JsonResponse({
            'success': False,
            'message': f'Minimum cart total of NPR {coupon.min_purchase_amount} required to use this coupon.'
        })

    discount = coupon.calculate_discount(cart_total)
    new_total = max(0.0, cart_total - float(discount))

    return JsonResponse({
        'success': True,
        'message': f'Coupon "{coupon.code}" applied successfully!',
        'code': coupon.code,
        'discount_amount': round(float(discount), 2),
        'new_total': round(new_total, 2)
    })


# ==============================================================================
# SUPER ADMIN LOGIN & DASHBOARD (JAZZMIN THEME INSPIRED)
# ==============================================================================
def superadmin_login(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        return redirect('superadmin_dashboard')

    if request.method == 'POST':
        identity = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=identity, password=password)
        if not user:
            # Fallback to look up user by email
            u_obj = User.objects.filter(email__iexact=identity).first()
            if u_obj:
                user = authenticate(request, username=u_obj.username, password=password)

        if user and (user.is_superuser or user.is_staff):
            login(request, user)
            messages.success(request, f"Welcome Super Admin, {user.username}!")
            return redirect('superadmin_dashboard')
        else:
            messages.error(request, "Invalid superuser credentials or insufficient permissions.")

    return render(request, 'superadmin/login.html')


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_dashboard(request):
    # Analytics Metrics
    total_users_count = User.objects.count()
    total_sellers_count = SellerProfile.objects.count()
    pending_sellers_count = SellerProfile.objects.filter(status='pending').count()
    total_products_count = Product.objects.count()
    active_products_count = Product.objects.filter(is_active=True).count()
    
    if Order is not None:
        orders_qs = Order.objects.all()
        total_orders_count = orders_qs.count()
        completed_orders_count = orders_qs.count()
        try:
            total_revenue = orders_qs.aggregate(sum=Sum('total_amount'))['sum'] or 0
        except Exception:
            total_revenue = 0
        try:
            recent_orders = orders_qs.order_by('-created_at')[:10]
        except Exception:
            recent_orders = []
    else:
        total_orders_count = 0
        completed_orders_count = 0
        recent_orders = []

    active_offers_count = Offer.objects.filter(is_active=True, status='approved').count()
    active_coupons_count = Coupon.objects.filter(status='active').count()

    sellers_list = SellerProfile.objects.select_related('user').order_by('-id')[:15]
    all_products = Product.objects.select_related('category').prefetch_related('seller_request__seller').order_by('-id')[:20]
    all_offers = Offer.objects.select_related('created_by', 'seller').prefetch_related('products').order_by('-created_at')
    all_coupons = Coupon.objects.all().order_by('-created_at')

    # Pending approvals for admin review
    from seller.models import ProductRequest
    pending_product_requests = ProductRequest.objects.filter(status='pending').select_related('seller', 'category', 'product').order_by('-created_at')
    pending_offers_list = Offer.objects.filter(status='pending').select_related('seller').prefetch_related('products').order_by('-created_at')

    # Category Sales Breakdown for Analytics Chart
    categories = Category.objects.annotate(prod_count=Count('products')).order_by('-prod_count')[:6]
    cat_names = [c.name for c in categories]
    cat_counts = [c.prod_count for c in categories]

    # Admin Offer Form & Coupon Form
    admin_offer_form = AdminOfferForm()
    coupon_form = CouponForm()

    if request.method == 'POST':
        if 'action_create_offer' in request.POST:
            admin_offer_form = AdminOfferForm(request.POST)
            if admin_offer_form.is_valid():
                offer = admin_offer_form.save(commit=False)
                offer.created_by = request.user
                offer.status = 'approved'
                offer.is_active = True
                offer.save()
                admin_offer_form.save_m2m()
                messages.success(request, f"Admin Offer '{offer.title}' created successfully across selected products!")
                return redirect('superadmin_dashboard')
        elif 'action_create_coupon' in request.POST:
            coupon_form = CouponForm(request.POST)
            if coupon_form.is_valid():
                coupon = coupon_form.save()
                messages.success(request, f"Coupon '{coupon.code}' created and deployed successfully!")
                return redirect('superadmin_dashboard')
            else:
                errs = ", ".join([f"{k}: {v[0]}" for k, v in coupon_form.errors.items()])
                messages.error(request, f"Failed to deploy coupon: {errs}")

    return render(request, 'superadmin/dashboard.html', {
        'active_page': 'dashboard',
        'total_users_count': total_users_count,
        'total_sellers_count': total_sellers_count,
        'pending_sellers_count': pending_sellers_count,
        'total_products_count': total_products_count,
        'active_products_count': active_products_count,
        'total_orders_count': total_orders_count,
        'completed_orders_count': completed_orders_count,
        'total_revenue': total_revenue,
        'active_offers_count': active_offers_count,
        'active_coupons_count': active_coupons_count,
        'sellers_list': sellers_list,
        'all_products': all_products,
        'all_offers': all_offers,
        'pending_offers_list': pending_offers_list,
        'pending_product_requests': pending_product_requests,
        'all_coupons': all_coupons,
        'recent_orders': recent_orders,
        'cat_names_json': json.dumps(cat_names),
        'cat_counts_json': json.dumps(cat_counts),
        'admin_offer_form': admin_offer_form,
        'coupon_form': coupon_form,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_sellers(request):
    sellers_qs = SellerProfile.objects.select_related('user').order_by('-id')
    paginator = Paginator(sellers_qs, 30)
    page_number = request.GET.get('page')
    sellers_list = paginator.get_page(page_number)
    return render(request, 'superadmin/sellers.html', {
        'active_page': 'sellers',
        'sellers_list': sellers_list,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_analytics(request):
    cat_data = Category.objects.annotate(prod_count=Count('products')).order_by('-prod_count')[:10]
    cat_names = [c.name for c in cat_data if c.prod_count > 0]
    cat_counts = [c.prod_count for c in cat_data if c.prod_count > 0]

    order_status_labels = []
    order_status_counts = []
    if Order is not None:
        status_stats = Order.objects.values('status').annotate(cnt=Count('id'))
        order_status_labels = [s['status'].capitalize() for s in status_stats]
        order_status_counts = [s['cnt'] for s in status_stats]

    payment_labels = []
    payment_counts = []
    if Order is not None:
        pay_stats = Order.objects.values('payment_method').annotate(cnt=Count('id'))
        payment_labels = [p['payment_method'].upper() for p in pay_stats]
        payment_counts = [p['cnt'] for p in pay_stats]

    seller_data = SellerProfile.objects.annotate(p_count=Count('product_requests')).order_by('-p_count')[:7]
    seller_names = [s.shop_name for s in seller_data]
    seller_counts = [s.p_count for s in seller_data]

    total_revenue = 0
    total_orders = 0
    if Order is not None:
        total_revenue = Order.objects.filter(Q(status='completed') | Q(status='delivered') | Q(payment_status='paid')).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = Order.objects.count()

    return render(request, 'superadmin/analytics.html', {
        'active_page': 'analytics',
        'cat_names_json': json.dumps(cat_names),
        'cat_counts_json': json.dumps(cat_counts),
        'order_status_labels_json': json.dumps(order_status_labels),
        'order_status_counts_json': json.dumps(order_status_counts),
        'payment_labels_json': json.dumps(payment_labels),
        'payment_counts_json': json.dumps(payment_counts),
        'seller_names_json': json.dumps(seller_names),
        'seller_counts_json': json.dumps(seller_counts),
        'total_revenue': total_revenue,
        'total_orders': total_orders,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_products(request):
    sort = request.GET.get('sort', 'latest')
    if sort == 'alpha_asc':
        order_by_clause = 'title'
    elif sort == 'alpha_desc':
        order_by_clause = '-title'
    elif sort == 'oldest':
        order_by_clause = 'created_at'
    elif sort == 'price_low':
        order_by_clause = 'price'
    elif sort == 'price_high':
        order_by_clause = '-price'
    else:
        order_by_clause = '-created_at'

    all_products_qs = Product.objects.select_related('category').prefetch_related('seller_request__seller').order_by(order_by_clause)
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(all_products_qs, 30)
    page_number = request.GET.get('page')
    all_products = paginator.get_page(page_number)
    return render(request, 'superadmin/products.html', {
        'active_page': 'products',
        'all_products': all_products,
        'categories': categories,
        'current_sort': sort,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_add_product(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        brand_name = request.POST.get('brand_name', '').strip()
        category_id = request.POST.get('category_id')
        mrp = request.POST.get('mrp', 0)
        price = request.POST.get('price', 0)
        stock = request.POST.get('stock', 10)
        seller_name = request.POST.get('seller_name', 'SuperAdmin / Direct Store').strip()
        description = request.POST.get('description', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true'

        if not title or not brand_name or not category_id:
            messages.error(request, "Title, Brand Name, and Category are required fields.")
            return redirect('superadmin_products')

        category = get_object_or_404(Category, pk=category_id)

        try:
            mrp_val = float(mrp)
            price_val = float(price)
            stock_val = int(stock)
        except (ValueError, TypeError):
            messages.error(request, "Invalid numeric values for MRP, Price, or Stock.")
            return redirect('superadmin_products')

        product = Product.objects.create(
            title=title,
            brand_name=brand_name,
            category=category,
            mrp=mrp_val,
            price=price_val,
            stock=stock_val,
            seller_name=seller_name or "SuperAdmin / Direct Store",
            description=description,
            is_active=is_active,
        )

        if image_url:
            from product.models import ProductColor, ProductImage
            col = ProductColor.objects.create(
                product=product,
                color_name="Default",
                color_code="#000000",
                is_default=True
            )
            ProductImage.objects.create(
                color_variant=col,
                image_url=image_url,
                angle_label="Front View",
                order=0
            )

        messages.success(request, f"Product '{product.title}' created and added to catalog successfully!")
    return redirect('superadmin_products')


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        brand_name = request.POST.get('brand_name', '').strip()
        category_id = request.POST.get('category_id')
        mrp = request.POST.get('mrp', 0)
        price = request.POST.get('price', 0)
        stock = request.POST.get('stock', 0)
        seller_name = request.POST.get('seller_name', '').strip()
        description = request.POST.get('description', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true'

        if not title or not brand_name or not category_id:
            messages.error(request, "Title, Brand Name, and Category are required fields.")
            return redirect('superadmin_products')

        category = get_object_or_404(Category, pk=category_id)

        try:
            mrp_val = float(mrp)
            price_val = float(price)
            stock_val = int(stock)
        except (ValueError, TypeError):
            messages.error(request, "Invalid numeric values for MRP, Price, or Stock.")
            return redirect('superadmin_products')

        product.title = title
        product.brand_name = brand_name
        product.category = category
        product.mrp = mrp_val
        product.price = price_val
        product.stock = stock_val
        if seller_name:
            product.seller_name = seller_name
        product.description = description
        product.is_active = is_active
        product.save()

        if image_url:
            from product.models import ProductColor, ProductImage
            default_col = product.colors.filter(is_default=True).first() or product.colors.first()
            if not default_col:
                default_col = ProductColor.objects.create(
                    product=product,
                    color_name="Default",
                    color_code="#000000",
                    is_default=True
                )
            img_obj = default_col.images.first()
            if img_obj:
                img_obj.image_url = image_url
                img_obj.save()
            else:
                ProductImage.objects.create(
                    color_variant=default_col,
                    image_url=image_url,
                    angle_label="Front View",
                    order=0
                )

        messages.success(request, f"Product '{product.title}' updated successfully!")
    return redirect('superadmin_products')


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    title = product.title
    if hasattr(product, 'seller_request') and product.seller_request:
        product.seller_request.delete()
    product.delete()
    messages.success(request, f"Product '{title}' permanently deleted from catalog.")
    return redirect('superadmin_products')


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_product_reviews(request):
    from seller.models import ProductRequest
    pending_product_requests_qs = ProductRequest.objects.filter(status='pending').select_related('seller', 'category', 'product').order_by('-created_at')
    paginator = Paginator(pending_product_requests_qs, 30)
    page_number = request.GET.get('page')
    pending_product_requests = paginator.get_page(page_number)
    return render(request, 'superadmin/product_reviews.html', {
        'active_page': 'product_reviews',
        'pending_product_requests': pending_product_requests,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_coupons(request):
    coupon_form = CouponForm()
    if request.method == 'POST' and 'action_create_coupon' in request.POST:
        coupon_form = CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon = coupon_form.save()
            messages.success(request, f"Coupon '{coupon.code}' created and deployed successfully!")
            return redirect('superadmin_coupons')
        else:
            errs = ", ".join([f"{k}: {v[0]}" for k, v in coupon_form.errors.items()])
            messages.error(request, f"Failed to deploy coupon: {errs}")

    all_coupons_qs = Coupon.objects.all().order_by('-created_at')
    paginator = Paginator(all_coupons_qs, 30)
    page_number = request.GET.get('page')
    all_coupons = paginator.get_page(page_number)
    return render(request, 'superadmin/coupons.html', {
        'active_page': 'coupons',
        'coupon_form': coupon_form,
        'all_coupons': all_coupons,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_promotions(request):
    admin_offer_form = AdminOfferForm()
    if request.method == 'POST' and 'action_create_offer' in request.POST:
        admin_offer_form = AdminOfferForm(request.POST)
        if admin_offer_form.is_valid():
            offer = admin_offer_form.save(commit=False)
            offer.created_by = request.user
            offer.status = 'approved'
            offer.is_active = True
            offer.save()
            admin_offer_form.save_m2m()
            messages.success(request, f"Admin Offer '{offer.title}' created successfully across selected products!")
            return redirect('superadmin_promotions')

    all_offers_qs = Offer.objects.select_related('created_by', 'seller').prefetch_related('products').order_by('-created_at')
    paginator = Paginator(all_offers_qs, 30)
    page_number = request.GET.get('page')
    all_offers = paginator.get_page(page_number)
    pending_offers_list = Offer.objects.filter(status='pending').select_related('seller').prefetch_related('products').order_by('-created_at')
    return render(request, 'superadmin/promotions.html', {
        'active_page': 'promotions',
        'admin_offer_form': admin_offer_form,
        'all_offers': all_offers,
        'pending_offers_list': pending_offers_list,
    })


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_orders(request):
    if Order is not None:
        sort = request.GET.get('sort', 'latest')
        if sort == 'alpha_asc':
            order_by_clause = 'order_number'
        elif sort == 'alpha_desc':
            order_by_clause = '-order_number'
        elif sort == 'oldest':
            order_by_clause = 'created_at'
        elif sort == 'total_high':
            order_by_clause = '-total_amount'
        elif sort == 'total_low':
            order_by_clause = 'total_amount'
        else:
            order_by_clause = '-created_at'

        orders_qs = Order.objects.all().order_by(order_by_clause)
        paginator = Paginator(orders_qs, 30)
        page_number = request.GET.get('page')
        all_orders = paginator.get_page(page_number)
    else:
        all_orders = []
    return render(request, 'superadmin/orders.html', {
        'active_page': 'orders',
        'all_orders': all_orders,
        'current_sort': sort,
    })


# ==============================================================================
# SUPER ADMIN CONTROLS (Pause/Unpause/Delete Coupons, Approve Sellers, Offers, Products)
# ==============================================================================
@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_toggle_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    if coupon.status == 'active':
        coupon.status = 'paused'
        messages.info(request, f"Coupon '{coupon.code}' is now PAUSED.")
    else:
        coupon.status = 'active'
        messages.success(request, f"Coupon '{coupon.code}' is now ACTIVE.")
    coupon.save()
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_coupons'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, pk=coupon_id)
    code = coupon.code
    coupon.delete()
    messages.success(request, f"Coupon '{code}' deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_coupons'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    title = offer.title
    offer.delete()
    messages.success(request, f"Offer '{title}' deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_promotions'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_approve_offer(request, offer_id, action):
    offer = get_object_or_404(Offer, pk=offer_id)
    if action == 'approve':
        offer.status = 'approved'
        offer.is_active = True
        messages.success(request, f"Offer '{offer.title}' has been APPROVED and activated.")
    elif action == 'reject':
        offer.status = 'rejected'
        offer.is_active = False
        messages.warning(request, f"Offer '{offer.title}' has been REJECTED.")
    offer.save()
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_promotions'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_approve_product_request(request, req_id, action):
    from seller.models import ProductRequest
    req = get_object_or_404(ProductRequest, pk=req_id)
    if action == 'approve':
        req.approve_and_sync_product()
        messages.success(request, f"Product Request '{req.title}' has been APPROVED & synced.")
    elif action == 'reject':
        req.status = 'rejected'
        if req.product:
            req.product.is_active = False
            req.product.save()
        req.save()
        messages.warning(request, f"Product Request '{req.title}' has been REJECTED.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_products'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_approve_seller(request, seller_id, action):
    seller = get_object_or_404(SellerProfile, pk=seller_id)
    if action == 'approve':
        seller.status = 'approved'
        seller.is_verified = True
        messages.success(request, f"Seller '{seller.shop_name}' approved!")
    elif action == 'reject':
        seller.status = 'rejected'
        seller.is_verified = False
        messages.warning(request, f"Seller '{seller.shop_name}' rejected.")
    seller.save()
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_sellers'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_update_seller_status(request, seller_id):
    seller = get_object_or_404(SellerProfile, pk=seller_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'approved', 'rejected']:
            seller.status = new_status
            if new_status == 'approved':
                seller.is_verified = True
            elif new_status == 'rejected':
                seller.is_verified = False
            seller.save()
            messages.success(request, f"Seller '{seller.shop_name}' status set to {new_status.upper()}.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_sellers'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_toggle_product_status(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.is_active = not product.is_active
    product.save()
    status_str = "LIVE & ACTIVE" if product.is_active else "INACTIVE & UNPUBLISHED"
    messages.success(request, f"Product '{product.title}' status changed to {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_products'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_toggle_offer_status(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    offer.is_active = not offer.is_active
    offer.save()
    status_str = "ACTIVE" if offer.is_active else "PAUSED"
    messages.info(request, f"Offer '{offer.title}' is now {status_str}.")
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_promotions'))


@user_passes_test(is_super_admin, login_url='superadmin_login')
def superadmin_update_order_status(request, order_id):
    if Order is None:
        messages.error(request, "Order module unavailable.")
        return redirect(request.META.get('HTTP_REFERER', 'superadmin_orders'))
    
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')
        
        valid_statuses = [c[0] for c in Order.STATUS_CHOICES]
        valid_payment_statuses = [c[0] for c in Order.PAYMENT_STATUS_CHOICES]
        
        if new_status and new_status in valid_statuses:
            order.status = new_status
        if new_payment_status and new_payment_status in valid_payment_statuses:
            order.payment_status = new_payment_status
            
        order.save()
        messages.success(request, f"Order #{order.order_number} status updated to '{order.status.upper()}' (Payment: '{order.payment_status.upper()}').")
    
    return redirect(request.META.get('HTTP_REFERER', 'superadmin_orders'))
