# ALX Travel App - Chapa API Integration

This project demonstrates the integration of the Chapa API for payment processing in a Django-based travel booking application. Users can make bookings with secure payment options, and the system handles payment initiation, verification, and status updates.

## Features

- **Payment Model**: Comprehensive payment tracking with status management
- **Booking System**: Travel booking management with payment integration
- **Chapa API Integration**: Secure payment processing with Chapa
- **Webhook Support**: Real-time payment status updates
- **Background Tasks**: Email notifications using Celery
- **Admin Interface**: Easy management of payments and bookings

## Prerequisites

- Python 3.8+
- Django 5.2+
- Redis (for Celery)
- Chapa API account

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd alx_travel_app_0x02/alx_travel_app
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Chapa API Configuration
CHAPA_SECRET_KEY=your_chapa_secret_key_here
CHAPA_WEBHOOK_SECRET=your_webhook_secret_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### 3. Chapa API Setup

1. Create an account at [Chapa Developer Portal](https://developer.chapa.co/)
2. Obtain your API keys from the dashboard
3. Update the `.env` file with your actual API keys
4. Configure webhook endpoints in your Chapa dashboard

### 4. Database Setup

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 5. Start Services

#### Start Redis (for Celery)
```bash
redis-server
```

#### Start Celery Worker
```bash
celery -A travel_project worker --loglevel=info
```

#### Start Django Development Server
```bash
python3 manage.py runserver
```

## API Endpoints

### Payment Endpoints

#### 1. Initiate Payment
- **URL**: `POST /api/payment/initiate/`
- **Description**: Initiates a new payment with Chapa API
- **Request Body**:
```json
{
    "user_id": 1,
    "booking_reference": "BK12345678",
    "amount": "50000.00",
    "currency": "NGN",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Payment initiated successfully",
    "data": {
        "payment_id": "uuid-here",
        "payment_url": "https://checkout.chapa.co/...",
        "transaction_id": "TX_BK12345678_1234567890",
        "chapa_reference": "chapa-ref-here"
    }
}
```

#### 2. Verify Payment
- **URL**: `POST /api/payment/verify/`
- **Description**: Verifies payment status with Chapa API
- **Request Body**:
```json
{
    "transaction_id": "TX_BK12345678_1234567890"
}
```

#### 3. Payment Status
- **URL**: `GET /api/payment/status/<payment_id>/`
- **Description**: Get payment status for a specific payment
- **Authentication**: Required (login_required)

#### 4. User Payments
- **URL**: `GET /api/payment/user/`
- **Description**: Get all payments for the authenticated user
- **Authentication**: Required (login_required)

#### 5. Chapa Webhook
- **URL**: `POST /api/payment/webhook/`
- **Description**: Handles Chapa webhook notifications
- **Authentication**: None (webhook endpoint)

## Models

### Payment Model
- `id`: UUID primary key
- `user`: Foreign key to User model
- `booking_reference`: Unique booking reference
- `amount`: Payment amount
- `currency`: Payment currency (default: NGN)
- `payment_status`: Payment status (pending, completed, failed, cancelled)
- `transaction_id`: Unique transaction identifier
- `chapa_reference`: Chapa API reference
- `payment_url`: Chapa checkout URL
- `created_at`: Payment creation timestamp
- `updated_at`: Last update timestamp
- `payment_date`: Payment completion date

### Booking Model
- `id`: UUID primary key
- `user`: Foreign key to User model
- `booking_reference`: Unique booking reference
- `destination`: Travel destination
- `travel_date`: Travel date
- `return_date`: Return date (optional)
- `number_of_travelers`: Number of travelers
- `total_amount`: Total booking amount
- `booking_status`: Booking status (pending, confirmed, cancelled)
- `payment`: One-to-one relationship with Payment model
- `created_at`: Booking creation timestamp
- `updated_at`: Last update timestamp

## Payment Workflow

1. **User creates a booking** → System generates unique booking reference
2. **Payment initiation** → User calls `/api/payment/initiate/` with booking details
3. **Chapa API call** → System makes request to Chapa to create payment
4. **Payment URL generation** → Chapa returns checkout URL
5. **User completes payment** → User redirected to Chapa checkout
6. **Webhook notification** → Chapa sends webhook to `/api/payment/webhook/`
7. **Status update** → System updates payment and booking status
8. **Email notification** → Confirmation email sent via Celery background task

## Testing

### Sandbox Environment
- Use Chapa's sandbox environment for testing
- Test payment initiation and verification
- Verify webhook handling
- Test error scenarios

### Test Data
```bash
# Create test user
python3 manage.py shell
from django.contrib.auth.models import User
user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
```

## Security Considerations

- Store API keys in environment variables
- Implement proper webhook signature verification
- Use HTTPS in production
- Validate all input data
- Implement rate limiting
- Log all payment activities

## Error Handling

The system handles various error scenarios:
- Invalid API responses from Chapa
- Network failures
- Invalid payment data
- User authentication errors
- Database transaction failures

## Monitoring and Logging

- Payment status tracking
- Transaction logging
- Error monitoring
- Webhook delivery confirmation
- Email delivery status

## Production Deployment

1. Set `DEBUG=False` in production
2. Use production database (PostgreSQL recommended)
3. Configure proper email backend
4. Set up Redis cluster for Celery
5. Implement proper logging
6. Use HTTPS for all endpoints
7. Set up monitoring and alerting

## Support

For issues related to:
- **Chapa API**: Contact Chapa support
- **Django Application**: Check Django documentation
- **Celery**: Refer to Celery documentation

## License

This project is part of the ALX Software Engineering program.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Screenshots

*Include screenshots here demonstrating:*
- Successful payment initiation
- Payment verification
- Payment status updates in the Payment model
- Admin interface showing payment records
