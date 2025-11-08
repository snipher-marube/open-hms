from django.core.management import call_command
from django.test import TestCase
from core.models import Clinic, User
from patients.models import Patient, MedicalRecord
from appointments.models import Appointment
from inventory.models import Supplier, Category, InventoryItem, StockTransaction
from prescriptions.models import Medicine
from billing.models import Bill, BillItem, Payment

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
        self.assertTrue(StockTransaction.objects.count() > 0)
        self.assertTrue(MedicalRecord.objects.count() > 0)
        self.assertTrue(Bill.objects.count() > 0)
        self.assertTrue(BillItem.objects.count() > 0)
        self.assertTrue(Payment.objects.count() > 0)
