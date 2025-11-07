from django.db.models.signals import post_save
from django.dispatch import receiver
from prescriptions.models import Prescription, PrescribedMedicine
from .models import StockTransaction, InventoryItem

@receiver(post_save, sender=Prescription)
def update_inventory_on_prescription_dispense(sender, instance, created, **kwargs):
    """
    Automatically deduct stock when a prescription is marked as dispensed
    """
    if instance.is_dispensed and not created:
        # Get all prescribed medicines for this prescription
        prescribed_medicines = instance.medicines.all()
        
        for prescribed_med in prescribed_medicines:
            # Find the inventory item for this medicine
            # You might want to implement a strategy for batch selection (FIFO, etc.)
            inventory_item = InventoryItem.objects.filter(
                medicine=prescribed_med.medicine,
                quantity__gte=prescribed_med.quantity,
                status='active'
            ).order_by('expiry_date').first()  # FIFO - use earliest expiry first
            
            if inventory_item:
                # Create stock transaction
                StockTransaction.objects.create(
                    inventory_item=inventory_item,
                    transaction_type='sale',
                    quantity=-prescribed_med.quantity,  # Negative for outgoing
                    unit_price=inventory_item.selling_price,
                    reference=f'Prescription #{instance.id}',
                    notes=f'Dispensed to {instance.patient}',
                    created_by=instance.doctor,
                    patient=instance.patient,
                    prescription=instance
                )