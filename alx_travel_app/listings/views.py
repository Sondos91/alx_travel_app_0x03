import os
import requests
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from .models import Payment, Booking
from django.contrib.auth.models import User

# Chapa API configuration
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY', 'your_chapa_secret_key_here')
CHAPA_BASE_URL = 'https://api.chapa.co/v1'
CHAPA_WEBHOOK_SECRET = os.getenv('CHAPA_WEBHOOK_SECRET', 'your_webhook_secret_here')

@csrf_exempt
@require_http_methods(["POST"])
def initiate_payment(request):
    """
    Initiate payment with Chapa API
    """
    try:
        data = json.loads(request.body)
        
        # Extract required fields
        user_id = data.get('user_id')
        booking_reference = data.get('booking_reference')
        amount = data.get('amount')
        currency = data.get('currency', 'NGN')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Validate required fields
        if not all([user_id, booking_reference, amount, email, first_name, last_name]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)
        
        # Get or create user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
        
        # Check if payment already exists
        if Payment.objects.filter(booking_reference=booking_reference).exists():
            return JsonResponse({
                'success': False,
                'message': 'Payment already initiated for this booking'
            }, status=400)
        
        # Prepare Chapa API request
        chapa_data = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": f"TX_{booking_reference}_{int(timezone.now().timestamp())}",
            "callback_url": f"{request.build_absolute_uri('/api/payment/verify/')}",
            "return_url": f"{request.build_absolute_uri('/payment/success/')}",
            "customization": {
                "title": "Travel Booking Payment",
                "description": f"Payment for booking {booking_reference}"
            }
        }
        
        # Make request to Chapa API
        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{CHAPA_BASE_URL}/transaction/initialize",
            json=chapa_data,
            headers=headers
        )
        
        if response.status_code == 200:
            chapa_response = response.json()
            
            # Create payment record
            payment = Payment.objects.create(
                user=user,
                booking_reference=booking_reference,
                amount=amount,
                currency=currency,
                payment_status='pending',
                chapa_reference=chapa_response.get('data', {}).get('reference'),
                payment_url=chapa_response.get('data', {}).get('checkout_url'),
                transaction_id=chapa_data['tx_ref']
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Payment initiated successfully',
                'data': {
                    'payment_id': str(payment.id),
                    'payment_url': payment.payment_url,
                    'transaction_id': payment.transaction_id,
                    'chapa_reference': payment.chapa_reference
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Chapa API error: {response.text}'
            }, status=response.status_code)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request):
    """
    Verify payment status with Chapa API
    """
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        
        if not transaction_id:
            return JsonResponse({
                'success': False,
                'message': 'Transaction ID is required'
            }, status=400)
        
        # Get payment record
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Payment not found'
            }, status=404)
        
        # Verify with Chapa API
        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}"
        }
        
        response = requests.get(
            f"{CHAPA_BASE_URL}/transaction/verify/{transaction_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            chapa_response = response.json()
            chapa_data = chapa_response.get('data', {})
            
            # Update payment status based on Chapa response
            if chapa_data.get('status') == 'success':
                payment.payment_status = 'completed'
                payment.payment_date = timezone.now()
                
                # Update booking status if it exists
                try:
                    booking = Booking.objects.get(booking_reference=payment.booking_reference)
                    booking.booking_status = 'confirmed'
                    booking.payment = payment
                    booking.save()
                except Booking.DoesNotExist:
                    pass  # Booking might not exist yet
                
                # Send confirmation email (using Celery for background task)
                from .tasks import send_payment_confirmation_email
                send_payment_confirmation_email.delay(payment.id)
                
            elif chapa_data.get('status') == 'failed':
                payment.payment_status = 'failed'
            else:
                payment.payment_status = 'pending'
            
            payment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Payment verification completed',
                'data': {
                    'payment_id': str(payment.id),
                    'payment_status': payment.payment_status,
                    'chapa_status': chapa_data.get('status'),
                    'amount': str(payment.amount),
                    'currency': payment.currency
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Chapa API error: {response.text}'
            }, status=response.status_code)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }, status=500)

@csrf_exempt
def chapa_webhook(request):
    """
    Handle Chapa webhook notifications
    """
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
    try:
        # Verify webhook signature (implement proper verification)
        signature = request.headers.get('Chapa-Signature')
        
        # For now, we'll process the webhook without signature verification
        # In production, implement proper signature verification
        
        data = json.loads(request.body)
        tx_ref = data.get('tx_ref')
        
        if not tx_ref:
            return JsonResponse({'message': 'Missing tx_ref'}, status=400)
        
        # Find payment by transaction ID
        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return JsonResponse({'message': 'Payment not found'}, status=404)
        
        # Update payment status
        status = data.get('status')
        if status == 'success':
            payment.payment_status = 'completed'
            payment.payment_date = timezone.now()
            
            # Update booking status
            try:
                booking = Booking.objects.get(booking_reference=payment.booking_reference)
                booking.booking_status = 'confirmed'
                booking.payment = payment
                booking.save()
            except Booking.DoesNotExist:
                pass
                
        elif status == 'failed':
            payment.payment_status = 'failed'
        
        payment.save()
        
        return JsonResponse({'message': 'Webhook processed successfully'})
        
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

@login_required
def payment_status(request, payment_id):
    """
    Get payment status for a specific payment
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'payment_id': str(payment.id),
                'booking_reference': payment.booking_reference,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'payment_status': payment.payment_status,
                'transaction_id': payment.transaction_id,
                'chapa_reference': payment.chapa_reference,
                'payment_url': payment.payment_url,
                'created_at': payment.created_at.isoformat(),
                'updated_at': payment.updated_at.isoformat(),
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

@login_required
def user_payments(request):
    """
    Get all payments for the authenticated user
    """
    try:
        payments = Payment.objects.filter(user=request.user)
        payments_data = []
        
        for payment in payments:
            payments_data.append({
                'payment_id': str(payment.id),
                'booking_reference': payment.booking_reference,
                'amount': str(payment.amount),
                'currency': payment.currency,
                'payment_status': payment.payment_status,
                'transaction_id': payment.transaction_id,
                'created_at': payment.created_at.isoformat(),
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None
            })
        
        return JsonResponse({
            'success': True,
            'data': payments_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
