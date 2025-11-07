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


def reports(request):
    """Advanced reporting view"""
    # Add your reporting logic here
    return render(request, 'core/reports.html')