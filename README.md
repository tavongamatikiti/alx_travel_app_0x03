# ALX Travel App 0x03 - Production Deployment with Chapa Payment Integration

A production-ready Django travel booking application with Chapa Payment Gateway, Celery task queues with RabbitMQ, and public Swagger API documentation.

## Project Overview

This project implements ALX Task 0x03 requirements: deploying a Django application with Celery background tasks, RabbitMQ message broker, and publicly accessible Swagger documentation. The application integrates Chapa Payment Gateway for secure Ethiopian payment processing with automated email notifications.

## Features

- **Property Listings Management**: Browse and search property listings with advanced filtering
- **Booking System**: Create and manage booking reservations
- **Review System**: Leave and view reviews for properties
- **Payment Integration**: Secure payment processing via Chapa API
  - Payment initiation with unique transaction references
  - Payment verification and status tracking
  - Automatic booking confirmation on successful payment
  - Idempotent payment operations to prevent duplicate charges
- **Email Notifications**: Asynchronous email confirmations using Celery
- **RESTful API**: Comprehensive API with Swagger documentation

## Technology Stack

- **Backend**: Django 5.2.7
- **REST Framework**: Django REST Framework 3.16.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Payment Gateway**: Chapa API (Ethiopian payment processor)
- **Task Queue**: Celery 5.5.3
- **Message Broker**: RabbitMQ (via CloudAMQP)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Deployment**: PythonAnywhere (recommended) / AWS / Heroku / DigitalOcean

## Project Structure

```
alx_travel_app_0x03/
├── listings/
│   ├── models.py           # Listing, Booking, Review, Payment models
│   ├── views.py            # ViewSets and payment API endpoints
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery tasks for email notifications
│   ├── urls.py             # URL routing
│   └── migrations/         # Database migrations
├── settings.py             # Django settings with Celery and email config
├── celery_app.py           # Celery application configuration
├── urls.py                 # Root URL configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── DEPLOYMENT.md           # PythonAnywhere deployment guide
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10+
- RabbitMQ message broker (CloudAMQP recommended for production)
- Chapa account with API credentials
- Gmail account with app-specific password (for email notifications)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/tavongamatikiti/alx_travel_app_0x03.git
   cd alx_travel_app_0x03
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the following:
   - `SECRET_KEY`: Django secret key
   - `CHAPA_SECRET_KEY`: Your Chapa API secret key
   - `CHAPA_PUBLIC_KEY`: Your Chapa API public key
   - `CELERY_BROKER_URL`: CloudAMQP RabbitMQ URL (amqps://...)
   - `EMAIL_HOST_USER`: Email address for sending notifications
   - `EMAIL_HOST_PASSWORD`: Email password/app password

5. **Set up RabbitMQ** (Production: use CloudAMQP)

   For local development, install RabbitMQ:
   ```bash
   # macOS
   brew install rabbitmq
   brew services start rabbitmq

   # Ubuntu/Debian
   sudo apt-get install rabbitmq-server
   sudo systemctl start rabbitmq-server

   # Or use CloudAMQP (Recommended for production)
   # Sign up at https://www.cloudamqp.com/
   # Get your amqps:// URL and add to .env
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Celery worker** (in a separate terminal)
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

### Swagger Documentation
Access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`

## API Endpoints

### Core Endpoints

- **Listings**: `/api/listings/` - GET, POST, PUT, PATCH, DELETE
- **Bookings**: `/api/bookings/` - GET, POST, PUT, PATCH, DELETE
- **Reviews**: `/api/reviews/` - GET, POST, PUT, PATCH, DELETE

### Payment Endpoints

#### Initiate Payment
```http
POST /api/payments/initiate/
```

**Request Body:**
```json
{
  "booking_id": "uuid-string",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "0911234567"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "checkout_url": "https://checkout.chapa.co/...",
    "payment_id": "uuid-string",
    "transaction_reference": "tx-abc123-booking-id"
  }
}
```

#### Verify Payment
```http
GET /api/payments/verify/?tx_ref=<transaction_reference>
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment verified and completed successfully",
  "data": {
    "payment_id": "uuid-string",
    "booking_id": "uuid-string",
    "payment_status": "completed",
    "amount": "1000.00",
    "transaction_id": "chapa-tx-id"
  }
}
```

## Payment Workflow

1. **User creates a booking** via `/api/bookings/` (status: `pending`)
2. **Initiate payment** via `/api/payments/initiate/` with the booking ID
3. **User redirected to Chapa** checkout page to complete payment
4. **After payment**, Chapa redirects user to callback URL `/api/payments/verify/`
5. **System verifies payment** with Chapa API
6. **On success**:
   - Payment status updated to `completed`
   - Booking status updated to `confirmed`
   - Confirmation email sent asynchronously via Celery
7. **On failure**:
   - Payment status updated to `failed`
   - Booking remains in `pending` status

## Models

### Payment Model

| Field | Type | Description |
|-------|------|-------------|
| payment_id | UUIDField | Primary key |
| booking | ForeignKey | Related booking |
| transaction_id | CharField | Chapa transaction ID |
| amount | DecimalField | Payment amount |
| currency | CharField | Currency code (ETB) |
| payment_status | CharField | pending/completed/failed/cancelled |
| payment_method | CharField | Payment method used |
| chapa_reference | CharField | Unique reference for Chapa |
| checkout_url | URLField | Chapa checkout URL |
| payment_date | DateTimeField | Completion timestamp |

## Testing the Payment Flow

### Using Chapa Sandbox

1. **Set up sandbox credentials** in `.env`:
   ```bash
   CHAPA_SECRET_KEY=your-sandbox-secret-key
   CHAPA_BASE_URL=https://api.chapa.co/v1
   ```

2. **Create a test booking**:
   ```bash
   curl -X POST http://localhost:8000/api/bookings/ \
     -H "Content-Type: application/json" \
     -d '{
       "listing": "listing-uuid",
       "user": 1,
       "check_in_date": "2025-12-01",
       "check_out_date": "2025-12-05",
       "number_of_guests": 2,
       "total_price": "1000.00"
     }'
   ```

3. **Initiate payment**:
   ```bash
   curl -X POST http://localhost:8000/api/payments/initiate/ \
     -H "Content-Type: application/json" \
     -d '{
       "booking_id": "booking-uuid",
       "email": "test@example.com",
       "first_name": "Test",
       "last_name": "User",
       "phone_number": "0911234567"
     }'
   ```

4. **Visit the checkout_url** returned in the response

5. **Complete payment** using Chapa test cards

6. **Verify payment** automatically happens via callback, or manually:
   ```bash
   curl http://localhost:8000/api/payments/verify/?tx_ref=<transaction_reference>
   ```

## Swagger Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Configuration

### Environment Variables

See `.env.example` for all required environment variables:

- **Django Settings**: SECRET_KEY, DEBUG, ALLOWED_HOSTS
- **Database**: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- **CORS**: CORS_ALLOWED_ORIGINS
- **Chapa**: CHAPA_SECRET_KEY, CHAPA_PUBLIC_KEY, CHAPA_BASE_URL, CHAPA_CALLBACK_URL
- **Email**: EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- **Celery**: CELERY_BROKER_URL, CELERY_RESULT_BACKEND

### Database Configuration

By default, the project uses SQLite for development. For production, uncomment the PostgreSQL configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='alx_travel_app_db'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}
```

## Security Considerations

- **API Keys**: Never commit `.env` file or expose API keys
- **HTTPS**: Use HTTPS in production for secure payment transactions
- **CORS**: Configure CORS_ALLOWED_ORIGINS appropriately for production
- **SECRET_KEY**: Use a strong, unique secret key in production
- **Email Passwords**: Use app-specific passwords for Gmail

## Troubleshooting

### Celery Not Processing Tasks

- **RabbitMQ Connection**: Ensure RabbitMQ is running and accessible
  - Local: Check `sudo systemctl status rabbitmq-server` (Linux) or `brew services list` (macOS)
  - CloudAMQP: Verify the `CELERY_BROKER_URL` amqps:// connection string is correct
- Check Celery worker logs for connection errors
- Verify `CELERY_BROKER_URL` format in `.env`:
  - Local: `amqp://guest:guest@localhost:5672//`
  - CloudAMQP: `amqps://username:password@host/vhost`

### Payment Initiation Fails

- Verify Chapa API credentials are correct (test vs production keys)
- Check that the booking exists and is in `pending` status
- Ensure Chapa callback URL is publicly accessible (use ngrok for local testing)
- Review application logs for detailed error messages
- Check Chapa API limits: title (16 chars), tx_ref (50 chars)

### Email Not Sending

- Check Gmail configuration: enable 2FA and use app-specific password
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in `.env`
- Check Celery worker logs for email task execution
- Ensure RabbitMQ is properly routing tasks to workers

### Swagger Not Accessible

- Ensure DEBUG=True for development or configure production Swagger access
- Check ALLOWED_HOSTS includes your domain
- Verify URL patterns are correctly configured in `urls.py`

## Deployment Guide

For production deployment to PythonAnywhere, see **[DEPLOYMENT.md](DEPLOYMENT.md)** for:
- Complete step-by-step deployment guide
- Environment variable configuration
- Static files setup
- Celery worker with RabbitMQ (CloudAMQP)
- Public Swagger documentation setup

## ALX Project Requirements (Task 0x03)

This project implements **ALX Task 0x03**: Deployment of Django Application with Celery and Public API Documentation

### ✅ Requirements Met:

**1. Cloud Deployment**
- ✅ Application deployed to cloud server (PythonAnywhere recommended)
- ✅ All environment variables configured securely on server
- ✅ Production-ready configuration with PostgreSQL support

**2. Celery with RabbitMQ**
- ✅ Celery workers configured with RabbitMQ message broker
- ✅ Background tasks (email notifications) working in production
- ✅ CloudAMQP integration for reliable message queuing

**3. Public Swagger Documentation**
- ✅ Swagger UI accessible at `/swagger/` endpoint
- ✅ ReDoc accessible at `/redoc/` endpoint
- ✅ Comprehensive API documentation for all endpoints

**4. Payment Integration**
- ✅ Chapa Payment Gateway integration
- ✅ Payment initiation and verification endpoints
- ✅ Automated email confirmations via Celery
- ✅ Secure webhook handling for payment callbacks

**5. Production Testing**
- ✅ All endpoints tested and functional in live environment
- ✅ Email notifications working asynchronously
- ✅ Payment flow validated with Chapa sandbox

## Contributing

This is an educational project for ALX Software Engineering program.

## License

This project is for educational purposes as part of the ALX Software Engineering program.

## Author

Tavonga Matikiti - [GitHub](https://github.com/tavongamatikiti)

## Acknowledgments

- ALX Africa for the project requirements
- Chapa for payment gateway integration
- Django and DRF communities for excellent documentation
