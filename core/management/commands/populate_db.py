import random
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from faker import Faker
from tqdm import tqdm
from core.models import Clinic, User
from patients.models import Patient, MedicalRecord
from appointments.models import Appointment
from inventory.models import Supplier, Category, InventoryItem, StockTransaction
from prescriptions.models import Medicine
from billing.models import Bill, BillItem, Payment
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Populates the database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Clinics
        self.stdout.write("Creating clinics...")
        clinics = []
        for _ in tqdm(range(5)):
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
        self.stdout.write("Creating doctors...")
        doctors = []
        for _ in tqdm(range(10)):
            doctor = User.objects.create_user(
                username=fake.user_name(),
                password='password',
                user_type='doctor',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            doctors.append(doctor)

        # Create Patients
        self.stdout.write("Creating patients...")
        patients = []
        for _ in tqdm(range(50)):
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
        self.stdout.write("Creating appointments...")
        for _ in tqdm(range(200)):
            Appointment.objects.create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                appointment_date=make_aware(fake.date_time_this_year()),
                status=random.choice(['scheduled', 'confirmed', 'completed', 'cancelled']),
                reason=fake.sentence(),
                clinic=random.choice(clinics),
                created_by=random.choice(doctors)
            )

        # Create Suppliers
        self.stdout.write("Creating suppliers...")
        suppliers = []
        for _ in tqdm(range(10)):
            supplier = Supplier.objects.create(
                name=fake.company(),
                contact_person=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
                address=fake.address()
            )
            suppliers.append(supplier)

        # Create Categories
        self.stdout.write("Creating categories...")
        categories = []
        for _ in tqdm(range(5)):
            category = Category.objects.create(
                name=fake.word(),
                description=fake.sentence()
            )
            categories.append(category)

        # Create Medicines
        self.stdout.write("Creating medicines...")
        medicines = []
        for _ in tqdm(range(100)):
            medicine = Medicine.objects.create(
                name=fake.word(),
                generic_name=fake.word(),
                manufacturer=fake.company(),
                description=fake.sentence(),
                dosage_form=random.choice(['Tablet', 'Capsule', 'Syrup', 'Injection']),
                strength=f"{random.randint(1, 1000)}mg"
            )
            medicines.append(medicine)

        # Create Inventory Items
        self.stdout.write("Creating inventory items...")
        inventory_items = []
        for _ in tqdm(range(200)):
            cost_price = fake.pydecimal(left_digits=2, right_digits=2, positive=True, min_value=1, max_value=100)
            selling_price = round(cost_price * fake.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=1, max_value=3), 2)
            item = InventoryItem.objects.create(
                medicine=random.choice(medicines),
                category=random.choice(categories),
                batch_number=fake.ean(length=13),
                expiry_date=fake.future_date(end_date='+2y'),
                quantity=random.randint(10, 200),
                cost_price=cost_price,
                selling_price=selling_price,
                supplier=random.choice(suppliers),
                min_stock_level=random.randint(5, 20),
                max_stock_level=random.randint(100, 500)
            )
            inventory_items.append(item)

        # Create Stock Transactions
        self.stdout.write("Creating stock transactions...")
        for _ in tqdm(range(500)):
            transaction_type = random.choice(['purchase', 'sale'])
            if transaction_type == 'purchase':
                inventory_item = random.choice(inventory_items)
                quantity = random.randint(10, 50)
            else:
                # Ensure there is enough stock for a sale
                inventory_item = InventoryItem.objects.filter(quantity__gt=5).order_by('?').first()
                if not inventory_item:
                    continue
                quantity = -random.randint(1, 5)

            try:
                StockTransaction.objects.create(
                    inventory_item=inventory_item,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    created_by=random.choice(doctors),
                    patient=random.choice(patients) if transaction_type == 'sale' else None
                )
            except ValidationError:
                continue

        # Create Medical Records
        self.stdout.write("Creating medical records...")
        for patient in tqdm(patients):
            for _ in range(random.randint(1, 5)):
                MedicalRecord.objects.create(
                    patient=patient,
                    doctor=random.choice(doctors),
                    symptoms=fake.text(),
                    diagnosis=fake.text(),
                    treatment=fake.text(),
                    notes=fake.text()
                )

        # Create Bills
        self.stdout.write("Creating bills...")
        bills = []
        for patient in tqdm(patients):
            for _ in range(random.randint(1, 3)):
                bill = Bill.objects.create(
                    patient=patient,
                    bill_number=fake.uuid4(),
                    due_date=fake.future_date(end_date='+30d'),
                    created_by=random.choice(doctors)
                )

                # Create Bill Items
                total_amount = 0
                for _ in range(random.randint(1, 5)):
                    unit_price = fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=10, max_value=500)
                    quantity = random.randint(1, 3)
                    amount = unit_price * quantity
                    BillItem.objects.create(
                        bill=bill,
                        description=fake.sentence(),
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=amount
                    )
                    total_amount += amount

                bill.total_amount = total_amount
                bill.save()
                bills.append(bill)

        # Create Payments
        self.stdout.write("Creating payments...")
        for bill in tqdm(bills):
            if random.choice([True, False]):
                payment_amount = bill.total_amount
                bill.status = 'paid'
            else:
                payment_amount = fake.pydecimal(left_digits=5, right_digits=2, positive=True, max_value=int(bill.total_amount))
                bill.status = 'partial'

            Payment.objects.create(
                bill=bill,
                amount=payment_amount,
                payment_method=random.choice(['cash', 'card']),
                reference_number=fake.uuid4()
            )
            bill.paid_amount = payment_amount
            bill.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with fake data.'))
