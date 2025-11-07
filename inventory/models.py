from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum, F
from prescriptions.models import Medicine
from core.models import User
from patients.models import Patient
import uuid

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"

class InventoryItem(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    )
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    received_date = models.DateField(default=timezone.now)
    min_stock_level = models.PositiveIntegerField(default=10)
    max_stock_level = models.PositiveIntegerField(default=100)
    location = models.CharField(max_length=100, blank=True)  # Shelf location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    barcode = models.CharField(max_length=100, blank=True, unique=True)
    
    def clean(self):
        """Validate the inventory item"""
        if self.expiry_date < timezone.now().date():
            raise ValidationError({'expiry_date': 'Expiry date cannot be in the past.'})
        
        if self.quantity < 0:
            raise ValidationError({'quantity': 'Quantity cannot be negative.'})
        
        if self.cost_price <= 0:
            raise ValidationError({'cost_price': 'Cost price must be greater than zero.'})
        
        if self.selling_price <= 0:
            raise ValidationError({'selling_price': 'Selling price must be greater than zero.'})
        
        if self.selling_price < self.cost_price:
            raise ValidationError({'selling_price': 'Selling price cannot be less than cost price.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        if not self.barcode:
            self.barcode = f"MED{self.medicine.id:06d}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.medicine.name} - Batch: {self.batch_number}"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock_level
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    @property
    def is_near_expiry(self):
        """Check if item expires within 30 days"""
        return self.expiry_date <= (timezone.now().date() + timezone.timedelta(days=30))
    
    @property
    def total_value(self):
        return self.quantity * self.cost_price
    
    @property
    def profit_margin(self):
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
    
    @classmethod
    def get_low_stock_items(cls):
        return cls.objects.filter(quantity__lte=models.F('min_stock_level'), status='active')
    
    @classmethod
    def get_expired_items(cls):
        return cls.objects.filter(expiry_date__lt=timezone.now().date(), status='active')
    
    @classmethod
    def get_near_expiry_items(cls, days=30):
        threshold_date = timezone.now().date() + timezone.timedelta(days=days)
        return cls.objects.filter(
            expiry_date__lte=threshold_date,
            expiry_date__gte=timezone.now().date(),
            status='active'
        )
    
    @classmethod
    def get_total_inventory_value(cls):
        result = cls.objects.filter(status='active').aggregate(
            total_value=Sum(F('quantity') * F('cost_price'))
        )
        return result['total_value'] or 0
    
    def get_usage_rate(self):
        """Calculate average monthly usage based on transaction history"""
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        usage = StockTransaction.objects.filter(
            inventory_item=self,
            transaction_type='sale',
            transaction_date__gte=six_months_ago
        ).aggregate(total_used=Sum('quantity'))
        
        total_used = usage['total_used'] or 0
        return total_used / 6  # Average monthly usage
    
    class Meta:
        ordering = ['medicine__name', 'expiry_date']
        unique_together = ['medicine', 'batch_number']

class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('write_off', 'Write Off'),
    )
    
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()  # Positive for incoming, negative for outgoing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)  # Invoice number, prescription ID, etc.
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    prescription = models.ForeignKey('prescriptions.Prescription', on_delete=models.SET_NULL, null=True, blank=True)
    
    def clean(self):
        """Validate stock transaction"""
        if self.transaction_type in ['sale', 'return', 'transfer', 'write_off']:
            if self.quantity > 0:
                raise ValidationError({
                    'quantity': f'Quantity must be negative for {self.transaction_type} transactions.'
                })
        
        if self.transaction_type in ['purchase', 'adjustment']:
            if self.quantity < 0:
                raise ValidationError({
                    'quantity': f'Quantity must be positive for {self.transaction_type} transactions.'
                })
        
        # Check stock availability for outgoing transactions
        if self.transaction_type in ['sale', 'transfer'] and self.inventory_item_id:
            current_stock = self.inventory_item.quantity
            if abs(self.quantity) > current_stock:
                raise ValidationError({
                    'quantity': f'Insufficient stock. Available: {current_stock}'
                })
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"ST{timezone.now().strftime('%y%m%d')}{StockTransaction.objects.count() + 1:04d}"
        
        if self.unit_price is None:
            if self.transaction_type == 'purchase':
                self.unit_price = self.inventory_item.cost_price
            else:
                self.unit_price = self.inventory_item.selling_price
        
        self.total_amount = abs(self.quantity) * self.unit_price
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update inventory quantity
        self.update_inventory()
    
    def update_inventory(self):
        """Update inventory quantity after transaction"""
        inventory_item = self.inventory_item
        if self.transaction_type in ['purchase', 'adjustment']:
            inventory_item.quantity += self.quantity
        elif self.transaction_type in ['sale', 'return', 'transfer', 'write_off']:
            inventory_item.quantity -= abs(self.quantity)
        
        # Update status if stock is depleted
        if inventory_item.quantity == 0:
            inventory_item.status = 'inactive'
        
        inventory_item.save()
    
    def delete(self, *args, **kwargs):
        """Reverse the transaction when deleted"""
        # Reverse the inventory update
        inventory_item = self.inventory_item
        if self.transaction_type in ['purchase', 'adjustment']:
            inventory_item.quantity -= self.quantity
        elif self.transaction_type in ['sale', 'return', 'transfer', 'write_off']:
            inventory_item.quantity += abs(self.quantity)
        
        inventory_item.save()
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.inventory_item.medicine.name}"
    
    class Meta:
        ordering = ['-transaction_date']

class StockAlert(models.Model):
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('expired', 'Expired'),
        ('near_expiry', 'Near Expiry'),
        ('over_stock', 'Over Stock'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.inventory_item.medicine.name}"
    
    class Meta:
        ordering = ['-created_at']

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    po_number = models.CharField(max_length=20, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = f"PO{timezone.now().strftime('%y%m%d')}{PurchaseOrder.objects.count() + 1:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"
    
    class Meta:
        ordering = ['-order_date']

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update purchase order total
        self.purchase_order.total_amount = self.purchase_order.items.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        self.purchase_order.save()
    
    def __str__(self):
        return f"{self.medicine.name} - {self.quantity} units"