from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send payment confirmation email to user
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        user = payment.user
        
        subject = f'Payment Confirmation - Booking {payment.booking_reference}'
        message = f"""
        Dear {user.first_name or user.username},
        
        Your payment has been successfully processed!
        
        Payment Details:
        - Booking Reference: {payment.booking_reference}
        - Amount: {payment.currency} {payment.amount}
        - Transaction ID: {payment.transaction_id}
        - Payment Date: {payment.payment_date}
        
        Thank you for choosing our travel services!
        
        Best regards,
        Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@travelapp.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return f"Confirmation email sent to {user.email}"
        
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"

@shared_task
def send_payment_failure_email(payment_id):
    """
    Send payment failure notification email to user
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        user = payment.user
        
        subject = f'Payment Failed - Booking {payment.booking_reference}'
        message = f"""
        Dear {user.first_name or user.username},
        
        Unfortunately, your payment could not be processed.
        
        Payment Details:
        - Booking Reference: {payment.booking_reference}
        - Amount: {payment.currency} {payment.amount}
        - Transaction ID: {payment.transaction_id}
        
        Please try again or contact our support team for assistance.
        
        Best regards,
        Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@travelapp.com',
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return f"Failure notification email sent to {user.email}"
        
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"
