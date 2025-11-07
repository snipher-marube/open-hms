from django.db import models
from django.utils import timezone
from core.models import User
from patients.models import Patient, MedicalRecord

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    dosage_form = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, null=True, blank=True)
    prescription_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    is_dispensed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Prescription for {self.patient} on {self.prescription_date}"

class PrescribedMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.medicine.name} for {self.prescription.patient}"