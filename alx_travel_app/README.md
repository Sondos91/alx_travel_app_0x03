# ALX Travel App - Background Task Management with Celery and Email Notifications

This project demonstrates the integration of the Chapa API for payment processing in a Django-based travel booking application, with background task management using Celery and RabbitMQ. Users can make bookings with secure payment options, and the system handles payment initiation, verification, status updates, and automated email notifications.

## Features

- **Payment Model**: Comprehensive payment tracking with status management
- **Booking System**: Travel booking management with payment integration
- **Chapa API Integration**: Secure payment processing with Chapa
- **Webhook Support**: Real-time payment status updates
- **Background Tasks**: Email notifications using Celery with RabbitMQ
- **Email Notifications**: Automated booking confirmations and payment confirmations
- **Admin Interface**: Easy management of payments and bookings

## Prerequisites

- Python 3.8+
- Django 5.2+
- RabbitMQ (for Celery message broker)
- Chapa API account

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd alx_travel_app_0x03/alx_travel_app
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

# RabbitMQ Configuration (for Celery)
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

### 3. RabbitMQ Setup

1. Install RabbitMQ on your system:
   ```bash
   # macOS (using Homebrew)
   brew install rabbitmq
   
   # Ubuntu/Debian
   sudo apt-get install rabbitmq-server
   
   # Start RabbitMQ service
   sudo systemctl start rabbitmq-server
   # or
   brew services start rabbitmq
   ```

2. Enable RabbitMQ management plugin:
   ```bash
   sudo rabbitmq-plugins enable rabbitmq_management
   ```

3. Access RabbitMQ management interface at: http://localhost:15672
   - Default credentials: guest/guest

### 4. Chapa API Setup

1. Create an account at [Chapa Developer Portal](https://developer.chapa.co/)
2. Obtain your API keys from the dashboard
3. Update the `.env` file with your actual API keys
4. Configure webhook endpoints in your Chapa dashboard

### 5. Database Setup

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 6. Start Services

#### Start RabbitMQ (if not running as service)
```bash
rabbitmq-server
```

#### Start Celery Worker
```bash
celery -A travel_project worker --loglevel=info
```

#### Start Celery Beat (for scheduled tasks, if needed)
```bash
celery -A travel_project beat --loglevel=info
```

#### Start Django Development Server
```bash
python3 manage.py runserver
```

## API Endpoints

### Booking Endpoints

#### 1. Create Booking
- **URL**: `POST /api/booking/`
- **Description**: Creates a new travel booking and triggers confirmation email
- **Request Body**:
```json
{
    "user_id": 1,
    "destination": "Paris, France",
    "travel_date": "2024-06-15",
    "return_date": "2024-06-22",
    "number_of_travelers": 2,
    "total_amount": "150000.00"
}
```
- **Response**:
```json
{
    "success": true,
    "message": "Booking created successfully",
    "data": {
        "booking_id": "uuid-here",
        "booking_reference": "BK12345678",
        "destination": "Paris, France",
        "travel_date": "2024-06-15",
        "return_date": "2024-06-22",
        "number_of_travelers": 2,
        "total_amount": "150000.00",
        "booking_status": "pending",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

#### 2. Get Booking Details
- **URL**: `GET /api/booking/<booking_id>/`
- **Description**: Retrieves details of a specific booking

#### 3. List User Bookings
- **URL**: `GET /api/booking/?user_id=1`
- **Description**: Lists all bookings for a specific user

### Payment Endpoints

#### 1. Initiate Payment
- **URL**: `POST /api/payment/initiate/`
- **Description**: Initiates a new payment with Chapa API
- **Request Body**:
```json
{
    "user_id": 1,
    "booking_reference": "BK12345678",
    "amount": "150000.00",
    "currency": "NGN",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### 2. Verify Payment
- **URL**: `POST /api/payment/verify/`
- **Description**: Verifies payment status with Chapa API

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

## Background Tasks with Celery

### Email Tasks

The application uses Celery to handle background email tasks:

1. **Booking Confirmation Email** (`send_booking_confirmation_email`):
   - Triggered when a new booking is created
   - Sent to the user with booking details
   - Includes instructions for payment completion

2. **Payment Confirmation Email** (`send_payment_confirmation_email`):
   - Triggered when payment is successfully completed
   - Sent to the user with payment confirmation details

3. **Payment Failure Email** (`send_payment_failure_email`):
   - Triggered when payment processing fails
   - Sent to the user with failure details and next steps

### Task Configuration

- **Message Broker**: RabbitMQ (AMQP protocol)
- **Result Backend**: RPC (Remote Procedure Call)
- **Task Serialization**: JSON
- **Task Time Limits**: 30 minutes (hard), 25 minutes (soft)
- **Timezone**: UTC

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

## Workflow

### Booking Workflow
1. **User creates a booking** → System generates unique booking reference
2. **Background task triggered** → Celery sends booking confirmation email
3. **Payment initiation** → User calls `/api/payment/initiate/` with booking details
4. **Chapa API call** → System makes request to Chapa to create payment
5. **Payment URL generation** → Chapa returns checkout URL
6. **User completes payment** → User redirected to Chapa checkout
7. **Webhook notification** → Chapa sends webhook to `/api/payment/webhook/`
8. **Status update** → System updates payment and booking status
9. **Email notification** → Payment confirmation email sent via Celery background task

### Email Workflow
1. **Task Creation**: Email tasks are created using `.delay()` method
2. **Task Queue**: Tasks are queued in RabbitMQ
3. **Worker Processing**: Celery workers pick up tasks from the queue
4. **Email Sending**: Django email backend sends emails
5. **Task Completion**: Task results are logged and monitored

## Testing

### Testing Background Tasks

1. **Start Celery Worker**:
   ```bash
   celery -A travel_project worker --loglevel=info
   ```

2. **Test Email Tasks**:
   ```bash
   # Create a test booking
   curl -X POST http://localhost:8000/api/booking/ \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "destination": "Test Destination",
       "travel_date": "2024-06-15",
       "total_amount": "50000.00"
     }'
   ```

3. **Monitor Celery Worker**: Watch the worker logs for task execution

### Testing Email Configuration

1. **Console Backend**: Emails are printed to console in development
2. **SMTP Backend**: Configure real SMTP settings for production testing

## Monitoring and Debugging

### Celery Monitoring

1. **Worker Status**: Check worker status with `celery -A travel_project status`
2. **Task Monitoring**: Monitor task execution in worker logs
3. **Queue Status**: Check RabbitMQ management interface for queue status

### Email Debugging

1. **Console Output**: Check console for email content in development
2. **Task Results**: Monitor task return values in Celery logs
3. **Error Handling**: Check task exception handling and logging

## Production Deployment

1. Set `DEBUG=False` in production
2. Use production database (PostgreSQL recommended)
3. Configure production email backend (SMTP or email service)
4. Set up RabbitMQ cluster for high availability
5. Implement proper logging and monitoring
6. Use HTTPS for all endpoints
7. Set up Celery monitoring (Flower recommended)
8. Configure task retry policies and error handling

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Failed**:
   - Check if RabbitMQ service is running
   - Verify connection URL in settings
   - Check firewall settings

2. **Celery Worker Not Starting**:
   - Verify Django settings configuration
   - Check Celery configuration in celery.py
   - Ensure all dependencies are installed

3. **Email Tasks Not Executing**:
   - Check Celery worker logs
   - Verify email configuration in settings
   - Check task registration and discovery

4. **Tasks Stuck in Queue**:
   - Check RabbitMQ queue status
   - Verify worker availability
   - Check task configuration and serialization

## Security Considerations

- Store API keys in environment variables
- Implement proper webhook signature verification
- Use HTTPS in production
- Validate all input data
- Implement rate limiting
- Log all payment activities
- Secure RabbitMQ access
- Monitor task execution and results

## Support

For issues related to:
- **Chapa API**: Contact Chapa support
- **Django Application**: Check Django documentation
- **Celery**: Refer to Celery documentation
- **RabbitMQ**: Check RabbitMQ documentation

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
- Successful booking creation
- Email task execution in Celery worker
- Payment initiation and verification
- Payment status updates in the Payment model
- Admin interface showing payment and booking records
- RabbitMQ management interface
