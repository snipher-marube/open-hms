from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm
from core.models import Clinic

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date')
    today = timezone.now().date()
    today_appointments = appointments.filter(appointment_date__date=today)
    upcoming_appointments = appointments.filter(appointment_date__date__gt=today)
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
    })

@login_required
def appointment_create(request):
    default_clinic = Clinic.objects.first()
    if not default_clinic:
        messages.error(request, "No clinic configured. Please contact administrator.")
        return redirect('appointment-list')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.clinic = default_clinic  # Set the clinic
            appointment.save()
            messages.success(request, 'Appointment created successfully.')
            return redirect('appointment-list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Create Appointment'})

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})

@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully.')
            return redirect('appointment-detail', pk=appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Update Appointment'})

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully.')
        return redirect('appointment-list')
    return render(request, 'appointments/appointment_confirm_delete.html', {'appointment': appointment})

@login_required
def appointment_update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}.')
        return redirect('appointment-detail', pk=appointment.pk)