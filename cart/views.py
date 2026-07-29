from django.shortcuts import render

def cart_view(request):
    return render(request, 'cart/cart.html')

def checkout_view(request):
    return render(request, 'cart/checkout.html')
