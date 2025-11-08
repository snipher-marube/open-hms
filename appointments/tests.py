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

class AppointmentListTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.clinic = Clinic.objects.create(name='Test Clinic', address='123 Test St', established_date=timezone.now())
        self.doctor1 = User.objects.create_user(username='doctor1', password='password', user_type='doctor', first_name='James', last_name='Smith')
        self.doctor2 = User.objects.create_user(username='doctor2', password='password', user_type='doctor', first_name='Maria', last_name='Garcia')
        self.patient1 = Patient.objects.create(first_name='John', last_name='Doe', date_of_birth='1990-01-01', clinic=self.clinic)
        self.patient2 = Patient.objects.create(first_name='Jane', last_name='Doe', date_of_birth='1992-02-02', clinic=self.clinic)

        now = timezone.now()
        self.appointment1 = Appointment.objects.create(patient=self.patient1, doctor=self.doctor1, appointment_date=now, status='scheduled', clinic=self.clinic, reason='test')
        self.appointment2 = Appointment.objects.create(patient=self.patient2, doctor=self.doctor2, appointment_date=now + timezone.timedelta(days=1), status='confirmed', clinic=self.clinic, reason='test')
        self.appointment3 = Appointment.objects.create(patient=self.patient1, doctor=self.doctor1, appointment_date=now + timezone.timedelta(days=2), status='completed', clinic=self.clinic, reason='test')
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')


    def test_filter_by_status(self):
        response = self.client.get(reverse('appointment-list'), {'status': 'scheduled'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0], self.appointment1)

    def test_filter_by_doctor(self):
        response = self.client.get(reverse('appointment-list'), {'doctor': self.doctor2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0], self.appointment2)

    def test_search_by_patient_name(self):
        response = self.client.get(reverse('appointment-list'), {'search_query': 'Jane'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0], self.appointment2)