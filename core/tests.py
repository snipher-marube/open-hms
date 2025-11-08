from django.core.management import call_command
from django.test import TestCase
from core.models import Clinic, User
from patients.models import Patient
from appointments.models import Appointment
from inventory.models import Supplier, Category, InventoryItem
from prescriptions.models import Medicine

class PopulateDbTestCase(TestCase):
    def test_populate_db_command(self):
        # Call the management command
        call_command('populate_db')

        # Assert that the correct number of objects have been created
        self.assertEqual(Clinic.objects.count(), 5)
        self.assertEqual(User.objects.filter(user_type='doctor').count(), 10)
        self.assertEqual(Patient.objects.count(), 50)
        self.assertEqual(Appointment.objects.count(), 200)
        self.assertEqual(Supplier.objects.count(), 10)
        self.assertEqual(Category.objects.count(), 5)
        self.assertEqual(Medicine.objects.count(), 100)
        self.assertEqual(InventoryItem.objects.count(), 200)
