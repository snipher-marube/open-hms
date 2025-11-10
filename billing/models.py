from django.db import models
from patients.models import Patient
from core.models import User

class Bill(models.Model):
    """
    Represents a bill for a patient.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    )

    bill_number = models.CharField(max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    bill_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        """
        Returns a string representation of the bill.
        """
        return f"Bill {self.bill_number} - {self.patient}"
    
    @property
    def balance_due(self):
        """
        Calculates the balance due on the bill.
        """
        return self.total_amount - self.paid_amount

class BillItem(models.Model):
    """
    Represents an item on a bill.
    """
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """
        Calculates the amount before saving.
        """
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Payment(models.Model):
    """
    Represents a payment made for a bill.
    """
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('insurance', 'Insurance'),
        ('online', 'Online Payment'),
    )
    
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        """
        Returns a string representation of the payment.
        """
        return f"Payment of {self.amount} for Bill {self.bill.bill_number}"

class MpesaPayment(models.Model):
    """
    Represents a payment made via M-Pesa.
    """
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100)
    merchant_request_id = models.CharField(max_length=100)
    response_code = models.CharField(max_length=10)
    response_description = models.CharField(max_length=200)
    customer_message = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the M-Pesa payment.
        """
        return f"MpesaPayment {self.checkout_request_id}"