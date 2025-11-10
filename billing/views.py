import json
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Bill, MpesaPayment
from .forms import BillForm
from mpesa_api.core import MpesaClient
from django.conf import settings

@login_required
def bill_list(request):
    """
    Renders the list of bills.
    """
    bills = Bill.objects.all()
    return render(request, 'billing/bill_list.html', {'bills': bills})

@login_required
def bill_detail(request, pk):
    """
    Renders the details of a single bill.
    """
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'billing/bill_detail.html', {'bill': bill})

@login_required
def bill_create(request):
    """
    Handles the creation of a new bill.
    """
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.save()
            return redirect('bill-detail', pk=bill.pk)
    else:
        form = BillForm()
    return render(request, 'billing/bill_form.html', {'form': form})

@login_required
def initiate_stk_push(request, pk):
    """
    Initiates an STK push for the specified bill.
    """
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = bill.balance_due

        mpesa_client = MpesaClient(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET,
            settings.MPESA_SHORTCODE,
            settings.MPESA_PASSKEY
        )

        callback_url = request.build_absolute_uri(reverse('mpesa_callback'))
        response = mpesa_client.lipa_na_mpesa_online(
            phone_number=phone_number,
            amount=int(amount),
            callback_url=callback_url,
            account_reference=bill.bill_number,
            transaction_desc='Hospital Bill Payment'
        )

        if response.get('ResponseCode') == '0':
            MpesaPayment.objects.create(
                bill=bill,
                phone_number=phone_number,
                amount=amount,
                checkout_request_id=response['CheckoutRequestID'],
                merchant_request_id=response['MerchantRequestID'],
                response_code=response['ResponseCode'],
                response_description=response['ResponseDescription'],
                customer_message=response['CustomerMessage']
            )
            bill.payment_status = 'pending'
            bill.save()
            messages.success(request, 'STK push initiated successfully.')
        else:
            messages.error(request, f"Error initiating STK push: {response.get('errorMessage')}")

        return redirect('bill-detail', pk=bill.pk)

@csrf_exempt
def mpesa_callback(request):
    """
    Handles the M-Pesa callback.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']
        result_code = data['Body']['stkCallback']['ResultCode']

        try:
            mpesa_payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
            bill = mpesa_payment.bill

            if result_code == 0:
                bill.paid_amount += mpesa_payment.amount
                bill.payment_status = 'successful'
                if bill.paid_amount >= bill.total_amount:
                    bill.status = 'paid'
                else:
                    bill.status = 'partial'
            else:
                bill.payment_status = 'failed'

            bill.save()
        except MpesaPayment.DoesNotExist:
            pass

        return JsonResponse({'status': 'ok'})
