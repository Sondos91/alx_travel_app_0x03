from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Payment, Booking
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Create test data for the payment system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create test user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Created test user: {user.username}')
        else:
            self.stdout.write(f'Test user already exists: {user.username}')
        
        # Create test booking
        booking, created = Booking.objects.get_or_create(
            booking_reference='BK12345678',
            defaults={
                'user': user,
                'destination': 'Lagos, Nigeria',
                'travel_date': '2024-12-25',
                'return_date': '2024-12-30',
                'number_of_travelers': 2,
                'total_amount': Decimal('50000.00'),
                'booking_status': 'pending'
            }
        )
        
        if created:
            self.stdout.write(f'Created test booking: {booking.booking_reference}')
        else:
            self.stdout.write(f'Test booking already exists: {booking.booking_reference}')
        
        # Create test payment
        payment, created = Payment.objects.get_or_create(
            booking_reference='BK12345678',
            defaults={
                'user': user,
                'amount': Decimal('50000.00'),
                'currency': 'NGN',
                'payment_status': 'pending',
                'transaction_id': f'TX_BK12345678_{int(uuid.uuid4().time)}',
                'chapa_reference': f'CHAPA_{uuid.uuid4().hex[:8].upper()}',
                'payment_url': 'https://checkout.chapa.co/test-payment-url'
            }
        )
        
        if created:
            self.stdout.write(f'Created test payment: {payment.id}')
        else:
            self.stdout.write(f'Test payment already exists: {payment.id}')
        
        # Link booking and payment
        if not booking.payment:
            booking.payment = payment
            booking.save()
            self.stdout.write('Linked booking and payment')
        
        self.stdout.write(self.style.SUCCESS('Test data creation completed!'))
        self.stdout.write(f'Admin URL: http://localhost:8000/admin/')
        self.stdout.write(f'Username: admin')
        self.stdout.write(f'Password: admin123')
