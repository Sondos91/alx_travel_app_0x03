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
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Payment, Booking
from django.contrib.auth.models import User

# Chapa API configuration
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY', 'your_chapa_secret_key_here')
CHAPA_BASE_URL = 'https://api.chapa.co/v1'
CHAPA_WEBHOOK_SECRET = os.getenv('CHAPA_WEBHOOK_SECRET', 'your_webhook_secret_here')

@extend_schema(
    operation_id='initiate_payment',
    summary='Initiate Payment',
    description='Initiate a payment transaction with Chapa API for a booking',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID of the user making the payment'},
                'booking_reference': {'type': 'string', 'description': 'Unique booking reference'},
                'amount': {'type': 'string', 'description': 'Payment amount'},
                'currency': {'type': 'string', 'description': 'Payment currency (default: NGN)'},
                'email': {'type': 'string', 'format': 'email', 'description': 'User email address'},
                'first_name': {'type': 'string', 'description': 'User first name'},
                'last_name': {'type': 'string', 'description': 'User last name'},
            },
            'required': ['user_id', 'booking_reference', 'amount', 'email', 'first_name', 'last_name']
        }
    },
    responses={
        200: {
            'description': 'Payment initiated successfully',
            'content': {
                'application/json': {
                    'example': {
                        'success': True,
                        'message': 'Payment initiated successfully',
                        'data': {
                            'payment_id': 'uuid-here',
                            'payment_url': 'https://checkout.chapa.co/...',
                            'transaction_id': 'TX_BK12345678_1234567890',
                            'chapa_reference': 'chapa-ref-here'
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request - Missing required fields'},
        404: {'description': 'User not found'},
        500: {'description': 'Internal server error'}
    },
    tags=['Payments']
)
@api_view(['POST'])
@permission_classes([AllowAny])
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

@extend_schema(
    operation_id='create_booking',
    summary='Create Booking',
    description='Create a new travel booking and trigger confirmation email',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID of the user making the booking'},
                'destination': {'type': 'string', 'description': 'Travel destination'},
                'travel_date': {'type': 'string', 'format': 'date', 'description': 'Travel date (YYYY-MM-DD)'},
                'return_date': {'type': 'string', 'format': 'date', 'description': 'Return date (YYYY-MM-DD) - optional'},
                'number_of_travelers': {'type': 'integer', 'description': 'Number of travelers (default: 1)'},
                'total_amount': {'type': 'string', 'description': 'Total booking amount'},
            },
            'required': ['user_id', 'destination', 'travel_date', 'total_amount']
        }
    },
    responses={
        200: {
            'description': 'Booking created successfully',
            'content': {
                'application/json': {
                    'example': {
                        'success': True,
                        'message': 'Booking created successfully',
                        'data': {
                            'booking_id': 'uuid-here',
                            'booking_reference': 'BK12345678',
                            'destination': 'Paris, France',
                            'travel_date': '2024-06-15',
                            'return_date': '2024-06-22',
                            'number_of_travelers': 2,
                            'total_amount': '150000.00',
                            'booking_status': 'pending',
                            'created_at': '2024-01-15T10:30:00Z'
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request - Missing required fields'},
        404: {'description': 'User not found'},
        500: {'description': 'Internal server error'}
    },
    tags=['Bookings']
)
@method_decorator(csrf_exempt, name='dispatch')
class BookingViewSet(View):
    """
    ViewSet for handling booking operations
    """
    
    def post(self, request):
        """
        Create a new booking
        """
        try:
            data = json.loads(request.body)
            
            # Extract required fields
            user_id = data.get('user_id')
            destination = data.get('destination')
            travel_date = data.get('travel_date')
            return_date = data.get('return_date')
            number_of_travelers = data.get('number_of_travelers', 1)
            total_amount = data.get('total_amount')
            
            # Validate required fields
            if not all([user_id, destination, travel_date, total_amount]):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required fields: user_id, destination, travel_date, total_amount'
                }, status=400)
            
            # Get user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'User not found'
                }, status=404)
            
            # Create booking
            booking = Booking.objects.create(
                user=user,
                destination=destination,
                travel_date=travel_date,
                return_date=return_date,
                number_of_travelers=number_of_travelers,
                total_amount=total_amount,
                booking_status='pending'
            )
            
            # Trigger background task to send booking confirmation email
            from .tasks import send_booking_confirmation_email
            send_booking_confirmation_email.delay(str(booking.id))
            
            return JsonResponse({
                'success': True,
                'message': 'Booking created successfully',
                'data': {
                    'booking_id': str(booking.id),
                    'booking_reference': booking.booking_reference,
                    'destination': booking.destination,
                    'travel_date': booking.travel_date.isoformat(),
                    'return_date': booking.return_date.isoformat() if booking.return_date else None,
                    'number_of_travelers': booking.number_of_travelers,
                    'total_amount': str(booking.total_amount),
                    'booking_status': booking.booking_status,
                    'created_at': booking.created_at.isoformat()
                }
            })
            
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
    
    def get(self, request, booking_id=None):
        """
        Get booking details or list all bookings for a user
        """
        if booking_id:
            # Get specific booking
            try:
                booking = get_object_or_404(Booking, id=booking_id)
                return JsonResponse({
                    'success': True,
                    'data': {
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'destination': booking.destination,
                        'travel_date': booking.travel_date.isoformat(),
                        'return_date': booking.return_date.isoformat() if booking.return_date else None,
                        'number_of_travelers': booking.number_of_travelers,
                        'total_amount': str(booking.total_amount),
                        'booking_status': booking.booking_status,
                        'payment_id': str(booking.payment.id) if booking.payment else None,
                        'created_at': booking.created_at.isoformat(),
                        'updated_at': booking.updated_at.isoformat()
                    }
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error retrieving booking: {str(e)}'
                }, status=500)
        else:
            # Get user_id from query params
            user_id = request.GET.get('user_id')
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'user_id parameter is required'
                }, status=400)
            
            try:
                bookings = Booking.objects.filter(user_id=user_id)
                bookings_data = []
                
                for booking in bookings:
                    bookings_data.append({
                        'booking_id': str(booking.id),
                        'booking_reference': booking.booking_reference,
                        'destination': booking.destination,
                        'travel_date': booking.travel_date.isoformat(),
                        'return_date': booking.return_date.isoformat() if booking.return_date else None,
                        'number_of_travelers': booking.number_of_travelers,
                        'total_amount': str(booking.total_amount),
                        'booking_status': booking.booking_status,
                        'created_at': booking.created_at.isoformat()
                    })
                
                return JsonResponse({
                    'success': True,
                    'data': bookings_data
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error retrieving bookings: {str(e)}'
                }, status=500)
