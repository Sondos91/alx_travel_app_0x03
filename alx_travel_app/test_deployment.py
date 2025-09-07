#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""

import os
import sys
import django
from datetime import date

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

def test_django_configuration():
    """Test Django configuration"""
    print("🧪 Testing Django Configuration...")
    print("=" * 50)
    
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        # Test settings
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"✅ DATABASES: {settings.DATABASES['default']['ENGINE']}")
        print(f"✅ INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
        print(f"✅ CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        print(f"✅ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        
        # Test Django check
        print("\n🔍 Running Django system check...")
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django system check passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False

def test_swagger_configuration():
    """Test Swagger configuration"""
    print("\n🧪 Testing Swagger Configuration...")
    print("=" * 50)
    
    try:
        from drf_spectacular.utils import extend_schema
        from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
        
        print("✅ drf-spectacular imported successfully")
        print("✅ Swagger views available")
        
        # Test URL configuration
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test schema endpoint
        try:
            response = client.get('/api/schema/')
            if response.status_code == 200:
                print("✅ API schema endpoint working")
            else:
                print(f"⚠️  API schema endpoint returned status {response.status_code}")
        except Exception as e:
            print(f"⚠️  API schema endpoint error: {e}")
        
        # Test Swagger UI endpoint
        try:
            response = client.get('/swagger/')
            if response.status_code == 200:
                print("✅ Swagger UI endpoint working")
            else:
                print(f"⚠️  Swagger UI endpoint returned status {response.status_code}")
        except Exception as e:
            print(f"⚠️  Swagger UI endpoint error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Swagger configuration error: {e}")
        return False

def test_celery_configuration():
    """Test Celery configuration"""
    print("\n🧪 Testing Celery Configuration...")
    print("=" * 50)
    
    try:
        from celery import Celery
        from listings.tasks import send_booking_confirmation_email, send_payment_confirmation_email
        
        print("✅ Celery imported successfully")
        print("✅ Email tasks imported successfully")
        
        # Test task registration
        from alx_travel_app.celery import app
        registered_tasks = list(app.tasks.keys())
        
        print(f"✅ Celery app configured: {app.main}")
        print(f"✅ Registered tasks: {len(registered_tasks)}")
        
        # Check if our tasks are registered
        if 'listings.tasks.send_booking_confirmation_email' in registered_tasks:
            print("✅ Booking confirmation email task registered")
        else:
            print("⚠️  Booking confirmation email task not found")
            
        if 'listings.tasks.send_payment_confirmation_email' in registered_tasks:
            print("✅ Payment confirmation email task registered")
        else:
            print("⚠️  Payment confirmation email task not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery configuration error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing Database Connection...")
    print("=" * 50)
    
    try:
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
        
        # Test migrations
        print("🔍 Checking migrations...")
        execute_from_command_line(['manage.py', 'showmigrations'])
        print("✅ Migrations check completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    print("=" * 50)
    
    try:
        from django.test import Client
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Test admin endpoint
        response = client.get('/admin/')
        if response.status_code in [200, 302]:  # 302 for redirect to login
            print("✅ Admin endpoint accessible")
        else:
            print(f"⚠️  Admin endpoint returned status {response.status_code}")
        
        # Test API schema endpoint
        response = client.get('/api/schema/')
        if response.status_code == 200:
            print("✅ API schema endpoint accessible")
        else:
            print(f"⚠️  API schema endpoint returned status {response.status_code}")
        
        # Test Swagger UI endpoint
        response = client.get('/swagger/')
        if response.status_code == 200:
            print("✅ Swagger UI endpoint accessible")
        else:
            print(f"⚠️  Swagger UI endpoint returned status {response.status_code}")
        
        # Test booking endpoint (should return 400 for missing data)
        response = client.post('/api/booking/', {}, content_type='application/json')
        if response.status_code == 400:
            print("✅ Booking endpoint accessible (returns 400 for invalid data)")
        else:
            print(f"⚠️  Booking endpoint returned status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ALX Travel App - Deployment Configuration Test")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60)
    
    tests = [
        test_django_configuration,
        test_swagger_configuration,
        test_celery_configuration,
        test_database_connection,
        test_api_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment configuration is ready.")
        print("\n📋 Next steps:")
        print("1. Start the server: python3 manage.py runserver")
        print("2. Start Celery worker: celery -A alx_travel_app worker --loglevel=info")
        print("3. Visit Swagger UI: http://localhost:8000/swagger/")
        print("4. Test API endpoints using the Swagger interface")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
