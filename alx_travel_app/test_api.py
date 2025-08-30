#!/usr/bin/env python3
"""
Test script for the Chapa API integration
This script demonstrates how to use the payment API endpoints
"""

import requests
import json
import time

# Configuration
BASE_URL = 'http://localhost:8000'
API_BASE = f'{BASE_URL}/api/payment'

def test_payment_initiation():
    """Test payment initiation endpoint"""
    print("Testing Payment Initiation...")
    
    payload = {
        "user_id": 1,
        "booking_reference": "BK12345678",
        "amount": "50000.00",
        "currency": "NGN",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    try:
        response = requests.post(f'{API_BASE}/initiate/', json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['data']['transaction_id']
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def test_payment_verification(transaction_id):
    """Test payment verification endpoint"""
    if not transaction_id:
        print("No transaction ID to verify")
        return
    
    print(f"\nTesting Payment Verification for {transaction_id}...")
    
    payload = {
        "transaction_id": transaction_id
    }
    
    try:
        response = requests.post(f'{API_BASE}/verify/', json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def test_payment_status(payment_id):
    """Test payment status endpoint"""
    if not payment_id:
        print("No payment ID to check")
        return
    
    print(f"\nTesting Payment Status for {payment_id}...")
    
    try:
        response = requests.get(f'{API_BASE}/status/{payment_id}/')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def test_webhook_simulation():
    """Simulate Chapa webhook notification"""
    print("\nSimulating Chapa Webhook...")
    
    # This is a sample webhook payload from Chapa
    webhook_payload = {
        "event": "charge.success",
        "data": {
            "id": "test_id",
            "tx_ref": "TX_BK12345678_1234567890",
            "flw_ref": "test_flw_ref",
            "amount": "50000.00",
            "currency": "NGN",
            "status": "success",
            "payment_type": "card",
            "customer": {
                "email": "test@example.com",
                "name": "John Doe"
            },
            "meta": {
                "booking_reference": "BK12345678"
            }
        }
    }
    
    try:
        response = requests.post(f'{API_BASE}/webhook/', json=webhook_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    """Main test function"""
    print("=" * 50)
    print("Chapa API Integration Test Script")
    print("=" * 50)
    
    # Test 1: Payment Initiation
    transaction_id = test_payment_initiation()
    
    if transaction_id:
        # Test 2: Payment Verification
        test_payment_verification(transaction_id)
        
        # Test 3: Webhook Simulation
        test_webhook_simulation()
        
        # Test 4: Payment Status (if we have a payment ID)
        # Note: In a real scenario, you'd get this from the payment initiation response
        print("\nNote: To test payment status, you need to create a payment first")
        print("and then use the payment ID from the initiation response")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
