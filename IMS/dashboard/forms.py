from django import forms
from .models import Products, StockMovements

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['sku', 'name', 'category', 'supplier', 'unit_cost', 'unit_price']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., ELEC-ACC-005'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'supplier': forms.Select(attrs={'class': 'form-input'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }

class StockMovementForm(forms.ModelForm):
    MOVEMENT_CHOICES = [
        ('IN', 'Restock / Arrival (IN)'),
        ('OUT', 'Sale / Dispatch (OUT)'),
        ('ADJUSTMENT', 'Stock adjustment (+/-)'),
    ]
    movement_type = forms.ChoiceField(choices=MOVEMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-input'}))
    
    class Meta:
        model = StockMovements
        fields = ['product', 'movement_type', 'quantity', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Optional reference details...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        quantity = cleaned_data.get('quantity')

        if quantity is not None:
            if movement_type == 'ADJUSTMENT' and quantity == 0:
                self.add_error('quantity', 'An adjustment must be a nonzero quantity.')
            elif movement_type in {'IN', 'OUT'} and quantity <= 0:
                self.add_error('quantity', 'Restock and dispatch quantities must be positive.')

        return cleaned_data