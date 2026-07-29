from django.shortcuts import render

def product_list(request):
    return render(request, 'product/product_list.html')

def product_detail(request, pk=None):
    return render(request, 'product/product_detail.html')
