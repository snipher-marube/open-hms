from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import InventoryItem, StockTransaction, Supplier, Category, PurchaseOrder, PurchaseOrderItem
from prescriptions.models import Medicine


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'generic_name', 'manufacturer', 'description', 'dosage_form', 'strength']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dosage_form': forms.TextInput(attrs={'class': 'form-control'}),
            'strength': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'medicine', 'category', 'batch_number', 'expiry_date', 'quantity',
            'cost_price', 'selling_price', 'supplier', 'min_stock_level',
            'max_stock_level', 'location', 'status'
        ]
        widgets = {
            'medicine': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'max_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default received date to today
        if not self.instance.pk:  # If creating new
            self.fields['expiry_date'].initial = timezone.now().date()
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data['expiry_date']
        if expiry_date and expiry_date < timezone.now().date():
            raise ValidationError("Expiry date cannot be in the past.")
        return expiry_date
    
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        selling_price = cleaned_data.get('selling_price')
        
        if cost_price and selling_price:
            if selling_price < cost_price:
                raise ValidationError({
                    'selling_price': 'Selling price cannot be less than cost price.'
                })
        
        return cleaned_data

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = [
            'inventory_item', 'transaction_type', 'quantity', 'unit_price',
            'reference', 'notes', 'patient', 'prescription'
        ]
        widgets = {
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active inventory items
        self.fields['inventory_item'].queryset = InventoryItem.objects.filter(status='active')
        
        # Set initial unit price based on transaction type - only if instance exists and has inventory_item
        if self.instance and self.instance.pk and hasattr(self.instance, 'inventory_item') and self.instance.inventory_item:
            if self.instance.transaction_type == 'purchase':
                self.fields['unit_price'].initial = self.instance.inventory_item.cost_price
            else:
                self.fields['unit_price'].initial = self.instance.inventory_item.selling_price
        else:
            # Set default unit price for new transactions based on selected inventory item
            self.fields['unit_price'].initial = 0
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        quantity = cleaned_data.get('quantity')
        inventory_item = cleaned_data.get('inventory_item')
        
        # Validate quantity based on transaction type
        if transaction_type and quantity is not None:
            if transaction_type in ['sale', 'return', 'transfer', 'write_off']:
                if quantity > 0:
                    raise ValidationError({
                        'quantity': f'Quantity must be negative for {transaction_type} transactions.'
                    })
            elif transaction_type in ['purchase', 'adjustment']:
                if quantity < 0:
                    raise ValidationError({
                        'quantity': f'Quantity must be positive for {transaction_type} transactions.'
                    })
        
        # Check stock availability for outgoing transactions
        if (transaction_type in ['sale', 'transfer'] and 
            inventory_item and quantity is not None):
            if abs(quantity) > inventory_item.quantity:
                raise ValidationError({
                    'quantity': f'Insufficient stock. Available: {inventory_item.quantity}'
                })
        
        return cleaned_data
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'expected_delivery', 'status', 'notes']
    
    def clean_expected_delivery(self):
        expected_delivery = self.cleaned_data['expected_delivery']
        order_date = self.cleaned_data['order_date']
        
        if expected_delivery and expected_delivery < order_date:
            raise ValidationError("Expected delivery date cannot be before order date.")
        
        return expected_delivery

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['medicine', 'quantity', 'unit_price']

class InventorySearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by medicine name, batch number, or category...'
    }))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(InventoryItem.STATUS_CHOICES),
        required=False
    )
    low_stock = forms.BooleanField(required=False, label='Show Low Stock Only')
    near_expiry = forms.BooleanField(required=False, label='Show Near Expiry Only')