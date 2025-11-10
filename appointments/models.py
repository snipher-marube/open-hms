from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import User, Clinic
from patients.models import Patient

class Appointment(models.Model):
    """
    Represents an appointment in the hospital management system.
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateTimeField()
    duration = models.PositiveIntegerField(default=30)  # Duration in minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_appointments', null=True, blank=True)
    
    def __str__(self):
        """
        Returns a string representation of the appointment.
        """
        return f"Appointment: {self.patient} with {self.doctor} on {self.appointment_date}"

    @property
    def end_time(self):
        """
        Calculates the end time of the appointment based on the appointment date and duration.
        """
        return self.appointment_date + timezone.timedelta(minutes=self.duration)

    def clean(self):
        """
        Prevents double booking for the same doctor or patient.
        """
        conflicting_appointments = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date__lt=self.end_time,
            appointment_date__gte=self.appointment_date
        ).exclude(pk=self.pk)

        if conflicting_appointments.exists():
            raise ValidationError(
                f"Dr. {self.doctor} already has an appointment scheduled at this time."
            )

        conflicting_patient_appointments = Appointment.objects.filter(
            patient=self.patient,
            appointment_date__lt=self.end_time,
            appointment_date__gte=self.appointment_date
        ).exclude(pk=self.pk)

        if conflicting_patient_appointments.exists():
            raise ValidationError(
                f"{self.patient} already has an appointment scheduled at this time."
            )

    class Meta:
        ordering = ['-appointment_date']
