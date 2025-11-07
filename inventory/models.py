from django.db import models
from django.utils import timezone
from prescriptions.models import Medicine

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    received_date = models.DateField(default=timezone.now)
    min_stock_level = models.PositiveIntegerField(default=10)
    
    def __str__(self):
        return f"{self.medicine.name} - Batch: {self.batch_number}"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock_level
    
    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    @classmethod
    def get_low_stock_items(cls):
        """Class method to get all low stock items"""
        return cls.objects.filter(quantity__lte=models.F('min_stock_level'))
    
    @classmethod
    def get_expired_items(cls):
        """Class method to get all expired items"""
        return cls.objects.filter(expiry_date__lt=timezone.now().date())

class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
    )
    
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.inventory_item.medicine.name}"