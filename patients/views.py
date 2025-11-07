from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, MedicalRecord, Clinic
from .forms import PatientForm, MedicalRecordForm

@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('-registration_date')
    return render(request, 'patients/patient_list.html', {'patients': patients})

@login_required
def patient_create(request):
    # Get the default clinic (you might want to make this configurable)
    default_clinic = Clinic.objects.first()
    
    if not default_clinic:
        messages.error(request, "No clinic configured. Please contact administrator.")
        return redirect('patient-list')
    
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.clinic = default_clinic  # Set the clinic
            patient.save()
            messages.success(request, f'Patient {patient.first_name} {patient.last_name} created successfully.')
            return redirect('patient-list')
    else:
        form = PatientForm()
    
    return render(request, 'patients/patient_form.html', {
        'form': form, 
        'title': 'Add Patient'
    })

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-visit_date')
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'medical_records': medical_records
    })

@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.first_name} {patient.last_name} updated successfully.')
            return redirect('patient-detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient'})

@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient deleted successfully.')
        return redirect('patient-list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})

@login_required
def medical_record_list(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-visit_date')
    return render(request, 'patients/medical_record_list.html', {
        'patient': patient,
        'medical_records': medical_records
    })

@login_required
def medical_record_create(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.patient = patient
            medical_record.doctor = request.user
            medical_record.save()
            messages.success(request, 'Medical record added successfully.')
            return redirect('patient-detail', pk=patient.pk)
    else:
        form = MedicalRecordForm()
    return render(request, 'patients/medical_record_form.html', {
        'form': form,
        'patient': patient,
        'title': 'Add Medical Record'
    })