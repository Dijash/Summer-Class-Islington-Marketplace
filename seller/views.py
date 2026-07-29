from django.shortcuts import render

def seller_dashboard(request):
    return render(request, 'seller/dashboard.html')

def add_product(request):
    return render(request, 'seller/add_product.html')

def manage_products(request):
    return render(request, 'seller/manage_products.html')
