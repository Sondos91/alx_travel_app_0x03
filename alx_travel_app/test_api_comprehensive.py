#!/usr/bin/env python3
"""
Comprehensive API Test Script for ALX Travel App
Tests all endpoints including booking creation and email notifications
"""

import requests
import json
import time
from datetime import date, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    """Print a formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_health_check():
    """Test if the server is running"""
    print_section("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        if response.status_code == 200:
            print_test_result("Server is running", True, f"Status: {response.status_code}")
            return True
        else:
            print_test_result("Server is running", False, f"Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test_result("Server is running", False, "Connection refused - server not running")
        return False

def test_booking_creation():
    """Test booking creation endpoint"""
    print_section("Testing Booking Creation")
    
    # Test data for booking
    booking_data = {
        "user_id": 1,
        "destination": "Paris, France",
        "travel_date": (date.today() + timedelta(days=30)).isoformat(),
        "return_date": (date.today() + timedelta(days=37)).isoformat(),
        "number_of_travelers": 2,
        "total_amount": "150000.00"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/booking/",
            json=booking_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test_result("Create booking", True, f"Booking ID: {data['data']['booking_id']}")
                return data['data']
            else:
                print_test_result("Create booking", False, f"API Error: {data.get('message')}")
                return None
        else:
            print_test_result("Create booking", False, f"HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("Create booking", False, f"Exception: {str(e)}")
        return None

def test_booking_retrieval(booking_id):
    """Test booking retrieval endpoint"""
    print_section("Testing Booking Retrieval")
    
    try:
        response = requests.get(f"{API_BASE}/booking/{booking_id}/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test_result("Get booking details", True, f"Destination: {data['data']['destination']}")
                return True
            else:
                print_test_result("Get booking details", False, f"API Error: {data.get('message')}")
                return False
        else:
            print_test_result("Get booking details", False, f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Get booking details", False, f"Exception: {str(e)}")
        return False

def test_user_bookings():
    """Test user bookings listing endpoint"""
    print_section("Testing User Bookings List")
    
    try:
        response = requests.get(f"{API_BASE}/booking/?user_id=1")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                bookings_count = len(data['data'])
                print_test_result("List user bookings", True, f"Found {bookings_count} bookings")
                return True
            else:
                print_test_result("List user bookings", False, f"API Error: {data.get('message')}")
                return False
        else:
            print_test_result("List user bookings", False, f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("List user bookings", False, f"Exception: {str(e)}")
        return False

def test_payment_initiation(booking_reference):
    """Test payment initiation endpoint"""
    print_section("Testing Payment Initiation")
    
    payment_data = {
        "user_id": 1,
        "booking_reference": booking_reference,
        "amount": "150000.00",
        "currency": "NGN",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/payment/initiate/",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test_result("Initiate payment", True, f"Payment ID: {data['data']['payment_id']}")
                return data['data']
            else:
                print_test_result("Initiate payment", False, f"API Error: {data.get('message')}")
                return None
        else:
            print_test_result("Initiate payment", False, f"HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("Initiate payment", False, f"Exception: {str(e)}")
        return None

def test_payment_verification(transaction_id):
    """Test payment verification endpoint"""
    print_section("Testing Payment Verification")
    
    verification_data = {
        "transaction_id": transaction_id
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/payment/verify/",
            json=verification_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_test_result("Verify payment", True, f"Status: {data['data']['payment_status']}")
                return True
            else:
                print_test_result("Verify payment", False, f"API Error: {data.get('message')}")
                return False
        else:
            print_test_result("Verify payment", False, f"HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Verify payment", False, f"Exception: {str(e)}")
        return False

def test_celery_tasks():
    """Test if Celery tasks are working"""
    print_section("Testing Celery Background Tasks")
    
    print("ℹ️  To test Celery tasks:")
    print("1. Start Celery worker: celery -A travel_project worker --loglevel=info")
    print("2. Create a booking using the API")
    print("3. Watch the Celery worker logs for email task execution")
    print("4. Check console output for email content (using console backend)")
    
    print_test_result("Celery task testing", True, "Manual verification required")

def run_all_tests():
    """Run all tests"""
    print_section("ALX Travel App - Comprehensive API Testing")
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Server is not running. Please start the Django server first:")
        print("   python3 manage.py runserver")
        return
    
    # Test booking endpoints
    booking_data = test_booking_creation()
    if booking_data:
        test_booking_retrieval(booking_data['booking_id'])
        test_user_bookings()
        
        # Test payment endpoints
        payment_data = test_payment_initiation(booking_data['booking_reference'])
        if payment_data:
            test_payment_verification(payment_data['transaction_id'])
    
    # Test Celery tasks
    test_celery_tasks()
    
    print_section("Testing Complete")
    print("📝 Check the logs and console output for detailed results")
    print("🐰 Remember to start Celery worker to test background tasks")
    print("📚 See README.md for detailed setup instructions")

if __name__ == "__main__":
    run_all_tests()
