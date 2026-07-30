from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
from .models import Product, ProductColor, ProductImage, ProductSize
from core.models import Category

def product_list(request):
    category_slug = request.GET.get('category')
    brand_query = request.GET.get('brand')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')
    selected_rating = request.GET.get('rating')
    sort_query = request.GET.get('sort')
    sale_query = request.GET.get('sale')

    products = Product.objects.filter(is_active=True)

    selected_category = None
    category_display_name = None

    if category_slug:
        cat_slug_lower = category_slug.lower()
        if cat_slug_lower in ['clothing', 'apparel']:
            clothing_slugs = ['dresses', 'kurtas-suit-sets', 'formal-menswear', 'denim-jeans', 'casual-shirts', 'tops-tees', 'jackets-coats', 'ethnic-wear', 'menswear', 'womenswear', 'activewear-gym', 'lingerie', 'indianwear']
            products = products.filter(Q(category__slug__in=clothing_slugs) | Q(category__name__icontains='wear') | Q(category__name__icontains='shirt') | Q(category__name__icontains='dress') | Q(category__name__icontains='jeans'))
            category_display_name = "Clothing"
        elif cat_slug_lower in ['shoes', 'footwear']:
            shoe_slugs = ['sneakers-kicks', 'footwear-loafers', 'his-footwear', 'her-footwear', 'nike', 'adidas', 'puma', 'puma-men']
            products = products.filter(Q(category__slug__in=shoe_slugs) | Q(category__name__icontains='footwear') | Q(category__name__icontains='sneaker') | Q(category__name__icontains='shoe'))
            category_display_name = "Shoes & Footwear"
        elif cat_slug_lower in ['accessories']:
            acc_slugs = ['handbags', 'luxury-handbags', 'eyewear', 'sunglasses-shades', 'jewellery-rings', 'watches', 'luxury-watches', 'luggage']
            products = products.filter(Q(category__slug__in=acc_slugs) | Q(category__name__icontains='watch') | Q(category__name__icontains='bag') | Q(category__name__icontains='eyewear') | Q(category__name__icontains='jewel'))
            category_display_name = "Accessories & Luggage"
        elif cat_slug_lower in ['beauty', 'beauty-makeup']:
            beauty_slugs = ['beauty-makeup', 'fragrances-perfume', 'lakme-maybelline']
            products = products.filter(Q(category__slug__in=beauty_slugs) | Q(category__name__icontains='beauty') | Q(category__name__icontains='perfume') | Q(category__name__icontains='makeup'))
            category_display_name = "Beauty & Cosmetics"
        elif cat_slug_lower in ['designers']:
            designer_brands = ['Gucci', 'Ralph Lauren', 'Calvin Klein', 'Hugo Boss', 'Diesel', 'Lacoste', 'Raymond', 'Zara', 'Tommy Hilfiger']
            products = products.filter(Q(brand_name__in=designer_brands) | Q(category__slug__icontains='luxury'))
            category_display_name = "Designer Brands"
        else:
            selected_category = Category.objects.filter(slug=category_slug).first()
            if selected_category:
                sub_ids = list(selected_category.subcategories.values_list('id', flat=True))
                category_ids = [selected_category.id] + sub_ids
                products = products.filter(category_id__in=category_ids)
                category_display_name = selected_category.name
            else:
                products = products.filter(Q(category__slug__icontains=category_slug) | Q(category__name__icontains=category_slug))
                category_display_name = category_slug.title()

    if sale_query and sale_query.lower() in ['true', '1', 'yes']:
        products = products.filter(mrp__gt=F('price'))
        category_display_name = "Sale & Special Offers"

    if brand_query:
        products = products.filter(brand_name__iexact=brand_query)

    if search_query:
        products = products.filter(title__icontains=search_query)

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if selected_color:
        products = products.filter(colors__color_name__icontains=selected_color)

    if selected_size:
        products = products.filter(sizes__size_label__iexact=selected_size)

    if selected_rating:
        try:
            products = products.filter(rating__gte=float(selected_rating))
        except ValueError:
            pass

    if sort_query == 'newest':
        products = products.order_by('-id')
        if not category_display_name:
            category_display_name = "New Arrivals"
    else:
        products = products.order_by('-id')

    products = products.distinct()

    # Fetch categories hierarchy with count
    parent_categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories').annotate(prod_count=Count('products'))
    all_categories = Category.objects.annotate(prod_count=Count('products')).filter(prod_count__gt=0)

    # Distinct Brands with count
    brands = Product.objects.values('brand_name').annotate(count=Count('id')).order_by('-count')[:12]

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product/product_list.html', {
        'page_obj': page_obj,
        'selected_category': selected_category,
        'category_display_name': category_display_name,
        'parent_categories': parent_categories,
        'all_categories': all_categories,
        'brands': brands,
        'min_price': min_price,
        'max_price': max_price,
        'selected_color': selected_color,
        'selected_size': selected_size,
        'selected_rating': selected_rating,
    })

def product_detail(request, pk=None, slug=None):
    if slug:
        product = get_object_or_404(Product, slug=slug)
    elif pk:
        product = get_object_or_404(Product, pk=pk)
    else:
        product = Product.objects.first()
        if not product:
            return render(request, 'product/product_detail.html', {'product': None})

    colors = product.colors.prefetch_related('images').all()
    sizes = product.sizes.all()
    default_color = colors.filter(is_default=True).first() or colors.first()

    return render(request, 'product/product_detail.html', {
        'product': product,
        'colors': colors,
        'sizes': sizes,
        'default_color': default_color,
    })
