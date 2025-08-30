#!/usr/bin/env python3
"""
Test script for Celery background tasks
This script tests the email notification tasks without requiring a full Django server
"""

import os
import sys
import django
from datetime import date

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_project.settings')
django.setup()

from listings.tasks import send_booking_confirmation_email, send_payment_confirmation_email
from listings.models import Booking, Payment, User
from django.utils import timezone

def test_celery_tasks():
    """Test Celery tasks execution"""
    print("Testing Celery Background Tasks...")
    print("=" * 50)
    
    try:
        # Check if we have any users
        users = User.objects.all()
        if not users.exists():
            print("No users found. Creating a test user...")
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            print(f"Created test user: {user.username}")
        else:
            user = users.first()
            print(f"Using existing user: {user.username}")
        
        # Check if we have any bookings
        bookings = Booking.objects.all()
        if not bookings.exists():
            print("No bookings found. Creating a test booking...")
            booking = Booking.objects.create(
                user=user,
                destination='Test Destination',
                travel_date=date(2024, 6, 15),
                return_date=date(2024, 6, 22),
                number_of_travelers=2,
                total_amount=150000.00,
                booking_status='pending'
            )
            print(f"Created test booking: {booking.booking_reference}")
        else:
            booking = bookings.first()
            print(f"Using existing booking: {booking.booking_reference}")
        
        # Check if we have any payments
        payments = Payment.objects.all()
        if not payments.exists():
            print("No payments found. Creating a test payment...")
            payment = Payment.objects.create(
                user=user,
                booking_reference=booking.booking_reference,
                amount=150000.00,
                currency='NGN',
                payment_status='completed',
                transaction_id=f"TX_{booking.booking_reference}_{int(timezone.now().timestamp())}",
                payment_date=timezone.now()
            )
            print(f"Created test payment: {payment.transaction_id}")
        else:
            payment = payments.first()
            print(f"Using existing payment: {payment.transaction_id}")
        
        print("\n" + "=" * 50)
        print("Testing Task Execution...")
        print("=" * 50)
        
        # Test booking confirmation email task
        print("\n1. Testing Booking Confirmation Email Task...")
        try:
            result = send_booking_confirmation_email.delay(str(booking.id))
            print(f"   Task ID: {result.id}")
            print(f"   Task Status: {result.status}")
            print("   ✓ Booking confirmation email task queued successfully")
        except Exception as e:
            print(f"   ✗ Error queuing booking confirmation email task: {e}")
        
        # Test payment confirmation email task
        print("\n2. Testing Payment Confirmation Email Task...")
        try:
            result = send_payment_confirmation_email.delay(str(payment.id))
            print(f"   Task ID: {result.id}")
            print(f"   Task Status: {result.status}")
            print("   ✓ Payment confirmation email task queued successfully")
        except Exception as e:
            print(f"   ✗ Error queuing payment confirmation email task: {e}")
        
        print("\n" + "=" * 50)
        print("Task Testing Complete!")
        print("=" * 50)
        print("\nTo see the actual task execution:")
        print("1. Start Celery worker: celery -A travel_project worker --loglevel=info")
        print("2. Run this test script again")
        print("3. Watch the Celery worker logs for task execution")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_celery_tasks()
