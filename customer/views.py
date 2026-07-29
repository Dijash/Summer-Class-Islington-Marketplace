from django.shortcuts import render

def dashboard(request):
    return render(request, 'customer/dashboard.html')

def orders(request):
    return render(request, 'customer/orders.html')
