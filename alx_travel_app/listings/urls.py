from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Payment API endpoints
    path('api/payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('api/payment/verify/', views.verify_payment, name='verify_payment'),
    path('api/payment/webhook/', views.chapa_webhook, name='chapa_webhook'),
    path('api/payment/status/<uuid:payment_id>/', views.payment_status, name='payment_status'),
    path('api/payment/user/', views.user_payments, name='user_payments'),
]
