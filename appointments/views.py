from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm
from core.models import Clinic, User
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date')

    # Filtering
    status = request.GET.get('status')
    doctor = request.GET.get('doctor')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if status:
        appointments = appointments.filter(status=status)
    if doctor:
        appointments = appointments.filter(doctor=doctor)
    if start_date and end_date:
        appointments = appointments.filter(appointment_date__range=[start_date, end_date])

    # Searching
    search_query = request.GET.get('search_query')
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(appointments, 10) # Show 10 appointments per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    doctors = User.objects.filter(user_type='doctor')

    # Preserve filters in pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()
    
    return render(request, 'appointments/appointment_list.html', {
        'page_obj': page_obj,
        'doctors': doctors,
        'status_choices': Appointment.STATUS_CHOICES,
        'filters': {
            'status': status,
            'doctor': doctor,
            'start_date': start_date,
            'end_date': end_date,
            'search_query': search_query,
        },
        'query_string': query_string
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
<<<<<<< HEAD
            appointment.clinic = default_clinic  # Set the clinic
=======
            appointment.clinic = default_clinic
            appointment.created_by = request.user
>>>>>>> f90b2db147130426127989ddb52e6cce5d321017
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
