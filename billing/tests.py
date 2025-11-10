from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from core.models import User, Clinic
from patients.models import Patient
from .models import Bill, BillItem
from unittest.mock import patch

class BillTestCase(TestCase):
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
        self.bill = Bill.objects.create(
            patient=self.patient,
            due_date=timezone.now(),
            created_by=self.user,
            bill_number='BILL-001'
        )
        BillItem.objects.create(
            bill=self.bill,
            description='Test Item',
            quantity=1,
            unit_price=100
        )

    def test_bill_creation(self):
        self.assertEqual(self.bill.total_amount, 0)
        self.assertEqual(self.bill.balance_due, 0)

    @patch('mpesa_api.core.MpesaClient.get_access_token')
    @patch('mpesa_api.core.MpesaClient.lipa_na_mpesa_online')
    def test_initiate_stk_push(self, mock_lipa_na_mpesa_online, mock_get_access_token):
        mock_get_access_token.return_value = 'test_access_token'
        mock_lipa_na_mpesa_online.return_value = {
            'ResponseCode': '0',
            'CheckoutRequestID': 'ws_CO_123456789',
            'MerchantRequestID': '12345-1234567-1',
            'ResponseDescription': 'Success. Request accepted for processing',
            'CustomerMessage': 'Success. Request accepted for processing'
        }
        response = self.client.post(reverse('initiate-stk-push', args=[self.bill.pk]), {'phone_number': '254712345678'})
        self.assertEqual(response.status_code, 302)
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.payment_status, 'pending')
