import requests
import base64
from datetime import datetime

class MpesaClient:
    def __init__(self, consumer_key, consumer_secret, shortcode, passkey):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.shortcode = shortcode
        self.passkey = passkey
        self.access_token = self.get_access_token()

    def get_access_token(self):
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        return response.json()['access_token']

    def lipa_na_mpesa_online(self, phone_number, amount, callback_url, account_reference, transaction_desc):
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f'{self.shortcode}{self.passkey}{timestamp}'.encode()).decode()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
