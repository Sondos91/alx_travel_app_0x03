from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    chapa_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.booking_reference} - {self.payment_status}"
    
    def get_status_display(self):
        return dict(self.PAYMENT_STATUS_CHOICES)[self.payment_status]

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    booking_reference = models.CharField(max_length=100, unique=True)
    destination = models.CharField(max_length=200)
    travel_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    number_of_travelers = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.destination}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"BK{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
