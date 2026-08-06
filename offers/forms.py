from django import forms
from .models import Offer, Coupon
from product.models import Product
from seller.models import ProductRequest

class SellerOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'offer_type', 'discount_value', 'products', 'is_active', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Summer Flash Sale 15%'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Offer description or terms'}),
            'offer_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'products': forms.CheckboxSelectMultiple(attrs={'class': 'product-checkbox-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        seller_profile = kwargs.pop('seller_profile', None)
        super().__init__(*args, **kwargs)
        if seller_profile:
            # Filter strictly ONLY accepted products belonging to this seller
            approved_product_ids = ProductRequest.objects.filter(
                seller=seller_profile,
                status='approved',
                product__isnull=False
            ).values_list('product_id', flat=True)
            
            self.fields['products'].queryset = Product.objects.filter(
                id__in=approved_product_ids,
                is_active=True
            )
        else:
            self.fields['products'].queryset = Product.objects.none()


class AdminOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'offer_type', 'discount_value', 'products', 'is_active', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SuperAdmin Site-wide Mega Discount'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'offer_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'products': forms.CheckboxSelectMultiple(attrs={'class': 'product-checkbox-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SuperAdmin can select ALL active products across the entire platform
        self.fields['products'].queryset = Product.objects.filter(is_active=True)


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'title', 'discount_type', 'discount_value', 'min_purchase_amount', 'max_discount_amount', 'usage_limit', 'status', 'valid_from', 'valid_to']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ISLINGTON20'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 20% Off Minimum Purchase of 1000'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False
        self.fields['status'].initial = 'active'
        self.fields['valid_from'].required = False
        self.fields['valid_to'].required = False
        self.fields['title'].required = False
        self.fields['max_discount_amount'].required = False
        self.fields['usage_limit'].required = False
        self.fields['min_purchase_amount'].required = False

    def clean_status(self):
        status = self.cleaned_data.get('status')
        return status if status else 'active'

