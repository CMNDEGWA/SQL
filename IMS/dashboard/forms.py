from django import forms
from .models import Products, StockMovements

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['sku', 'name', 'category', 'supplier', 'unit_cost', 'unit_price', 'quantity_in_stock']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., ELEC-ACC-005'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'supplier': forms.Select(attrs={'class': 'form-input'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}), 
        }

class StockMovementForm(forms.ModelForm):
    MOVEMENT_CHOICES = [
        ('IN', 'Restock / Arrival (IN)'),
        ('OUT', 'Sale / Dispatch (OUT)'),
    ]
    movement_type = forms.ChoiceField(choices=MOVEMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    
    class Meta:
        model = StockMovements
        fields = ['product', 'movement_type', 'quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional reference details...'}),
        }