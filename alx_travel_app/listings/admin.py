from django.contrib import admin
from .models import Payment, Booking

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'booking_reference', 'amount', 'currency', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'currency', 'created_at')
    search_fields = ('booking_reference', 'transaction_id', 'chapa_reference', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'booking_reference', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'transaction_id', 'chapa_reference', 'payment_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'payment_date'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'booking_reference', 'destination', 'travel_date', 'total_amount', 'booking_status', 'created_at')
    list_filter = ('booking_status', 'travel_date', 'created_at')
    search_fields = ('booking_reference', 'destination', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'booking_reference', 'destination')
        }),
        ('Travel Details', {
            'fields': ('travel_date', 'return_date', 'number_of_travelers', 'total_amount')
        }),
        ('Status', {
            'fields': ('booking_status', 'payment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
