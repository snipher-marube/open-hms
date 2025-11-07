from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from patients.models import Patient
from appointments.models import Appointment
from inventory.models import InventoryItem
from billing.models import Bill, Payment
import json

@login_required
def dashboard(request):
    # Basic statistics
    total_patients = Patient.objects.count()
    
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        appointment_date__date=today
    ).count()
    
    # Use the class method to get low stock items count
    low_stock_items = InventoryItem.get_low_stock_items().count()
    
    pending_bills = Bill.objects.filter(status='pending').count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-appointment_date')[:5]
    
    # Low stock items for display
    low_stock_items_list = InventoryItem.get_low_stock_items().select_related('medicine')[:5]
    
    # Chart data - Patient registrations by month (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # For SQLite (using strftime)
    patient_data = Patient.objects.filter(
        registration_date__gte=six_months_ago
    ).extra({
        'month': "strftime('%%Y-%%m', registration_date)"
    }).values('month').annotate(count=Count('id')).order_by('month')
    
    # For PostgreSQL (use this if you're using PostgreSQL):
    # patient_data = Patient.objects.filter(
    #     registration_date__gte=six_months_ago
    # ).annotate(
    #     month=TruncMonth('registration_date')
    # ).values('month').annotate(count=Count('id')).order_by('month')
    
    months = [item['month'] for item in patient_data]
    patient_counts = [item['count'] for item in patient_data]
    
    # Appointment statistics for chart
    appointment_status_data = Appointment.objects.values('status').annotate(
        count=Count('id')
    )
    
    status_labels = [item['status'] for item in appointment_status_data]
    status_counts = [item['count'] for item in appointment_status_data]
    
    # Revenue data (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    revenue_data = Payment.objects.filter(
        payment_date__gte=thirty_days_ago
    ).extra({
        'day': "strftime('%%Y-%%m-%%d', payment_date)"
    }).values('day').annotate(total=Sum('amount')).order_by('day')
    
    revenue_days = [item['day'] for item in revenue_data]
    revenue_totals = [float(item['total']) for item in revenue_data]
    
    context = {
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'low_stock_items': low_stock_items,
        'pending_bills': pending_bills,
        'recent_appointments': recent_appointments,
        'low_stock_items_list': low_stock_items_list,
        'months': json.dumps(months),
        'patient_counts': json.dumps(patient_counts),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'revenue_days': json.dumps(revenue_days),
        'revenue_totals': json.dumps(revenue_totals),
    }
    
    return render(request, 'core/dashboard.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta
import pandas as pd
import json
from patients.models import Patient, MedicalRecord
from appointments.models import Appointment
from inventory.models import InventoryItem, StockTransaction
from billing.models import Bill, Payment

@login_required
def reports(request):
    """Main reports dashboard"""
    context = {
        'report_types': [
            {'id': 'patient', 'name': 'Patient Reports', 'icon': '👥'},
            {'id': 'appointment', 'name': 'Appointment Reports', 'icon': '📅'},
            {'id': 'inventory', 'name': 'Inventory Reports', 'icon': '📦'},
            {'id': 'financial', 'name': 'Financial Reports', 'icon': '💰'},
            {'id': 'medical', 'name': 'Medical Reports', 'icon': '🏥'},
        ]
    }
    return render(request, 'core/reports.html', context)

@login_required
def generate_report(request, report_type):
    """Generate specific reports based on type"""
    
    # Date range handling
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = timezone.now().date()
    
    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    if report_type == 'patient':
        context.update(generate_patient_reports(start_date, end_date))
    elif report_type == 'appointment':
        context.update(generate_appointment_reports(start_date, end_date))
    elif report_type == 'inventory':
        context.update(generate_inventory_reports(start_date, end_date))
    elif report_type == 'financial':
        context.update(generate_financial_reports(start_date, end_date))
    elif report_type == 'medical':
        context.update(generate_medical_reports(start_date, end_date))
    
    format = request.GET.get('format', 'html')
    if format == 'pdf':
        return generate_pdf_report(context, report_type)
    elif format == 'excel':
        return generate_excel_report(context, report_type)
    
    return render(request, 'core/report_detail.html', context)

def generate_patient_reports(start_date, end_date):
    """Generate patient analytics reports"""
    # Patient registration trends
    registrations = Patient.objects.filter(
        registration_date__date__range=[start_date, end_date]
    ).extra({
        'month': "strftime('%%Y-%%m', registration_date)"
    }).values('month').annotate(count=Count('id')).order_by('month')
    
    # Patient demographics
    gender_distribution = Patient.objects.values('gender').annotate(
        count=Count('id')
    )
    
    age_groups = Patient.objects.extra({
        'age_group': """
            CASE 
                WHEN (strftime('%Y', 'now') - strftime('%Y', date_of_birth)) - 
                     (strftime('%m-%d', 'now') < strftime('%m-%d', date_of_birth)) < 18 THEN '0-17'
                WHEN (strftime('%Y', 'now') - strftime('%Y', date_of_birth)) - 
                     (strftime('%m-%d', 'now') < strftime('%m-%d', date_of_birth)) BETWEEN 18 AND 35 THEN '18-35'
                WHEN (strftime('%Y', 'now') - strftime('%Y', date_of_birth)) - 
                     (strftime('%m-%d', 'now') < strftime('%m-%d', date_of_birth)) BETWEEN 36 AND 50 THEN '36-50'
                ELSE '50+'
            END
        """
    }).values('age_group').annotate(count=Count('id'))
    
    # Top conditions
    top_conditions = MedicalRecord.objects.filter(
        visit_date__date__range=[start_date, end_date]
    ).values('diagnosis').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return {
        'registrations': list(registrations),
        'gender_distribution': list(gender_distribution),
        'age_groups': list(age_groups),
        'top_conditions': list(top_conditions),
        'total_patients': Patient.objects.count(),
        'new_patients': Patient.objects.filter(
            registration_date__date__range=[start_date, end_date]
        ).count(),
    }

def generate_appointment_reports(start_date, end_date):
    """Generate appointment analytics reports"""
    appointments = Appointment.objects.filter(
        appointment_date__date__range=[start_date, end_date]
    )
    
    # Status distribution
    status_distribution = appointments.values('status').annotate(
        count=Count('id')
    )
    
    # Doctor performance
    doctor_performance = appointments.values(
        'doctor__first_name', 'doctor__last_name'
    ).annotate(
        total_appointments=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
        cancellation_rate=Count('id', filter=Q(status='cancelled')) * 100.0 / Count('id')
    ).order_by('-total_appointments')
    
    # Daily appointment trends
    daily_trends = appointments.extra({
        'day': "strftime('%%Y-%%m-%%d', appointment_date)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    return {
        'status_distribution': list(status_distribution),
        'doctor_performance': list(doctor_performance),
        'daily_trends': list(daily_trends),
        'total_appointments': appointments.count(),
        'completion_rate': appointments.filter(status='completed').count() * 100.0 / appointments.count() if appointments.count() > 0 else 0,
    }

def generate_inventory_reports(start_date, end_date):
    """Generate inventory analytics reports"""
    # Stock movement
    transactions = StockTransaction.objects.filter(
        transaction_date__date__range=[start_date, end_date]
    )
    
    # Category distribution
    category_distribution = InventoryItem.objects.filter(status='active').values(
        'category__name'
    ).annotate(
        total_value=Sum('quantity') * Avg('cost_price'),
        total_items=Count('id')
    )
    
    # Stock alerts
    low_stock = InventoryItem.get_low_stock_items().count()
    near_expiry = InventoryItem.get_near_expiry_items().count()
    expired = InventoryItem.get_expired_items().count()
    
    # Top moving items
    top_moving = transactions.filter(transaction_type='sale').values(
        'inventory_item__medicine__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:10]
    
    return {
        'category_distribution': list(category_distribution),
        'low_stock_count': low_stock,
        'near_expiry_count': near_expiry,
        'expired_count': expired,
        'top_moving': list(top_moving),
        'total_inventory_value': InventoryItem.get_total_inventory_value(),
        'total_transactions': transactions.count(),
    }

def generate_financial_reports(start_date, end_date):
    """Generate financial analytics reports"""
    payments = Payment.objects.filter(
        payment_date__date__range=[start_date, end_date]
    )
    
    # Revenue by payment method
    revenue_by_method = payments.values('payment_method').annotate(
        total=Sum('amount')
    )
    
    # Monthly revenue
    monthly_revenue = payments.extra({
        'month': "strftime('%%Y-%%m', payment_date)"
    }).values('month').annotate(total=Sum('amount')).order_by('month')
    
    # Outstanding bills - calculate using the property
    pending_bills = Bill.objects.filter(status='pending')
    outstanding_bills = sum(bill.balance_due for bill in pending_bills)
    
    # Alternative approach using annotation (if you want to use database aggregation)
    # outstanding_bills = Bill.objects.filter(status='pending').aggregate(
    #     total=Sum(models.F('total_amount') - models.F('paid_amount'))
    # )['total'] or 0
    
    # Additional financial metrics
    total_bills = Bill.objects.filter(bill_date__date__range=[start_date, end_date]).count()
    paid_bills = Bill.objects.filter(status='paid', bill_date__date__range=[start_date, end_date]).count()
    pending_bills_count = Bill.objects.filter(status='pending', bill_date__date__range=[start_date, end_date]).count()
    
    # Payment trends by day
    daily_revenue = payments.extra({
        'day': "strftime('%%Y-%%m-%%d', payment_date)"
    }).values('day').annotate(total=Sum('amount')).order_by('day')
    
    return {
        'revenue_by_method': list(revenue_by_method),
        'monthly_revenue': list(monthly_revenue),
        'daily_revenue': list(daily_revenue),
        'outstanding_bills': outstanding_bills,
        'total_revenue': payments.aggregate(total=Sum('amount'))['total'] or 0,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'pending_bills_count': pending_bills_count,
        'payment_success_rate': (paid_bills * 100.0 / total_bills) if total_bills > 0 else 0,
    }

def generate_medical_reports(start_date, end_date):
    """Generate medical analytics reports"""
    medical_records = MedicalRecord.objects.filter(
        visit_date__date__range=[start_date, end_date]
    )
    
    # Common diagnoses
    common_diagnoses = medical_records.values('diagnosis').annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    # Treatment patterns
    treatment_patterns = medical_records.values('treatment').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Prescription analysis
    from prescriptions.models import Prescription
    prescriptions = Prescription.objects.filter(
        prescription_date__date__range=[start_date, end_date]
    )
    
    return {
        'common_diagnoses': list(common_diagnoses),
        'treatment_patterns': list(treatment_patterns),
        'total_visits': medical_records.count(),
        'total_prescriptions': prescriptions.count(),
        'prescription_rate': prescriptions.count() * 100.0 / medical_records.count() if medical_records.count() > 0 else 0,
    }

def generate_pdf_report(context, report_type):
    """Generate PDF report"""
    from django.template.loader import render_to_string
    from weasyprint import HTML
    import tempfile
    
    html_string = render_to_string('core/report_pdf.html', context)
    html = HTML(string=html_string)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().date()}.pdf"'
    
    html.write_pdf(response)
    return response

def generate_excel_report(context, report_type):
    """Generate Excel report"""
    import io
    from django.http import HttpResponse
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Create different sheets based on report type
        if report_type == 'patient':
            df = pd.DataFrame(context['registrations'])
            df.to_excel(writer, sheet_name='Patient Registrations', index=False)
            
            df_gender = pd.DataFrame(context['gender_distribution'])
            df_gender.to_excel(writer, sheet_name='Gender Distribution', index=False)
    
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().date()}.xlsx"'
    
    return response