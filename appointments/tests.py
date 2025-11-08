from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import User, Clinic
from patients.models import Patient
from .models import Appointment

class AppointmentCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.clinic = Clinic.objects.create(name='Test Clinic', address='123 Test St', established_date=timezone.now())
        self.user = User.objects.create_user(username='testuser', password='password')
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth='1990-01-01',
            clinic=self.clinic
        )
        self.client.login(username='testuser', password='password')

    def test_create_appointment(self):
        appointment_data = {
            'patient': self.patient.id,
            'doctor': self.user.id,
            'appointment_date': timezone.now(),
            'reason': 'Test Reason',
        }
        response = self.client.post(reverse('appointment-create'), data=appointment_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.exists())
