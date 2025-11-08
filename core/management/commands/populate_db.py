import random
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from faker import Faker
from core.models import Clinic, User
from patients.models import Patient
from appointments.models import Appointment

class Command(BaseCommand):
    help = 'Populates the database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Clinics
        clinics = []
        for _ in range(5):
            clinic = Clinic.objects.create(
                name=fake.company(),
                address=fake.address(),
                phone=fake.phone_number(),
                email=fake.email(),
                registration_number=fake.uuid4(),
                established_date=fake.date_this_century()
            )
            clinics.append(clinic)

        # Create Doctors
        doctors = []
        for _ in range(10):
            doctor = User.objects.create_user(
                username=fake.user_name(),
                password='password',
                user_type='doctor',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            doctors.append(doctor)

        # Create Patients
        patients = []
        for _ in range(50):
            patient = Patient.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(),
                gender=random.choice(['M', 'F', 'O']),
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
                clinic=random.choice(clinics)
            )
            patients.append(patient)

        # Create Appointments
        for _ in range(200):
            Appointment.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                appointment_date=make_aware(fake.date_time_this_year()),
                status=random.choice(['scheduled', 'confirmed', 'completed', 'cancelled']),
                reason=fake.sentence(),
                clinic=random.choice(clinics),
                created_by=random.choice(doctors)
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data.'))
