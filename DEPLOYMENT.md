# ALX Travel App 0x03 - PythonAnywhere Deployment Guide

This guide provides step-by-step instructions for deploying the Django application with Celery and RabbitMQ to PythonAnywhere.

## Prerequisites

- PythonAnywhere account (free or paid tier)
- CloudAMQP account (for RabbitMQ hosting - free tier available)
- Gmail account with App Password for email notifications
- Chapa API keys (for payment processing)

## Table of Contents

1. [Setup CloudAMQP (RabbitMQ)](#1-setup-cloudamqp-rabbitmq)
2. [Setup PythonAnywhere Account](#2-setup-pythonanywhere-account)
3. [Upload Code to PythonAnywhere](#3-upload-code-to-pythonanywhere)
4. [Configure Database](#4-configure-database)
5. [Setup Virtual Environment](#5-setup-virtual-environment)
6. [Configure Environment Variables](#6-configure-environment-variables)
7. [Configure WSGI](#7-configure-wsgi)
8. [Run Migrations](#8-run-migrations)
9. [Collect Static Files](#9-collect-static-files)
10. [Setup Celery Worker](#10-setup-celery-worker)
11. [Test Deployment](#11-test-deployment)

---

## 1. Setup CloudAMQP (RabbitMQ)

Since PythonAnywhere doesn't support running RabbitMQ directly, we'll use CloudAMQP (hosted RabbitMQ).

### Steps:

1. Go to https://www.cloudamqp.com/
2. Sign up for a free account
3. Create a new instance:
   - **Name**: alx-travel-app-rabbitmq
   - **Plan**: Little Lemur (Free)
   - **Region**: Choose closest to your users
4. Once created, go to the instance details
5. Copy the **AMQP URL** (looks like: `amqp://username:password@host.cloudamqp.com/vhost`)
6. Save this URL - you'll need it for environment variables

---

## 2. Setup PythonAnywhere Account

1. Go to https://www.pythonanywhere.com/
2. Sign up for an account (free or paid)
3. Log in to your dashboard

---

## 3. Upload Code to PythonAnywhere

### Option A: Using Git (Recommended)

1. Open a **Bash console** on PythonAnywhere
2. Clone your repository:
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/alx_travel_app_0x03.git
   cd alx_travel_app_0x03
   ```

### Option B: Upload via Files Tab

1. Go to the **Files** tab
2. Navigate to `/home/YOUR_USERNAME/`
3. Upload your project folder
4. Extract if uploaded as zip

---

## 4. Configure Database

PythonAnywhere provides MySQL for free tier users.

### Create Database:

1. Go to **Databases** tab
2. Create a new database:
   - **Database name**: `YOUR_USERNAME$alx_travel_db`
3. Set a database password
4. Note down the database details

### Update settings.py:

The database is already configured in `settings.py` to use environment variables.
You'll set these in step 6.

---

## 5. Setup Virtual Environment

In the Bash console:

```bash
cd ~/alx_travel_app_0x03

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Install MySQL client (for PythonAnywhere MySQL)
pip install mysqlclient
```

---

## 6. Configure Environment Variables

⚠️ **SECURITY WARNING**:
- NEVER commit the `.env` file with real credentials to GitHub!
- The `.env` file should only exist on the server, not in version control
- Only `.env.example` (with placeholder values) should be in GitHub

Create a `.env` file **directly on PythonAnywhere** (this stays on the server only):

```bash
cd ~/alx_travel_app_0x03
nano .env
```

Add the following (replace with your actual values):

```bash
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com

# Database Configuration (MySQL for PythonAnywhere)
DB_ENGINE=django.db.backends.mysql
DB_NAME=YOUR_USERNAME$alx_travel_db
DB_USER=YOUR_USERNAME
DB_PASSWORD=your-database-password
DB_HOST=YOUR_USERNAME.mysql.pythonanywhere-services.com
DB_PORT=3306

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com

# Chapa Payment Gateway
CHAPA_SECRET_KEY=your-chapa-secret-key
CHAPA_PUBLIC_KEY=your-chapa-public-key
CHAPA_BASE_URL=https://api.chapa.co/v1
CHAPA_CALLBACK_URL=https://YOUR_USERNAME.pythonanywhere.com/api/payments/verify/

# Email Configuration (Gmail with App Password)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Celery Configuration with CloudAMQP
CELERY_BROKER_URL=amqp://username:password@host.cloudamqp.com/vhost
CELERY_RESULT_BACKEND=rpc://
```

**Important Notes:**
- Replace `YOUR_USERNAME` with your PythonAnywhere username
- Use Gmail App Password, not regular password
- Use the CloudAMQP URL from step 1

Save and exit (Ctrl+X, then Y, then Enter in nano).

---

## 7. Configure WSGI

1. Go to the **Web** tab on PythonAnywhere
2. Click **Add a new web app**
3. Select **Manual configuration** (Python 3.10 or 3.11)
4. Click through the wizard

### Edit WSGI Configuration:

1. On the Web tab, find the **WSGI configuration file** link
2. Click to edit it
3. **Delete all contents** and replace with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/YOUR_USERNAME/alx_travel_app_0x03'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# Load environment variables
from pathlib import Path
import environ
env = environ.Env()
environ.Env.read_env(os.path.join(path, '.env'))

# Get the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Replace `YOUR_USERNAME` with your actual username
5. Save the file

### Configure Virtual Environment:

1. On the Web tab, find **Virtualenv** section
2. Enter: `/home/YOUR_USERNAME/alx_travel_app_0x03/venv`

### Configure Static Files:

1. On the Web tab, find **Static files** section
2. Add a new static file mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/alx_travel_app_0x03/staticfiles/`

---

## 8. Run Migrations

In the Bash console:

```bash
cd ~/alx_travel_app_0x03
source venv/bin/activate

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database with sample data (optional)
python manage.py seed
```

---

## 9. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This collects all static files (including Swagger UI) to the `staticfiles/` directory.

---

## 10. Setup Celery Worker

PythonAnywhere doesn't support long-running background processes on free tier, but you can run Celery in a few ways:

### Option A: Run Celery Worker Manually (Testing)

Open a new Bash console:

```bash
cd ~/alx_travel_app_0x03
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**Note**: This console must stay open. If you close it, the worker stops.

### Option B: Use Always-On Tasks (Paid Tier Only)

If you have a paid PythonAnywhere account:

1. Go to **Tasks** tab
2. Create a new scheduled task
3. Set it to run every hour:
   ```bash
   cd /home/YOUR_USERNAME/alx_travel_app_0x03 && /home/YOUR_USERNAME/alx_travel_app_0x03/venv/bin/celery -A celery_app worker --loglevel=info
   ```

### Option C: Use Task Scheduler for One-Off Tasks

For testing email notifications without a running worker:

```bash
cd ~/alx_travel_app_0x03
source venv/bin/activate
python manage.py shell

from listings.tasks import send_payment_confirmation_email
# Call the task directly (not via .delay())
send_payment_confirmation_email(payment_id, booking_id)
```

---

## 11. Test Deployment

### Reload Web App

1. Go to the **Web** tab
2. Click the green **Reload** button

### Test Swagger Documentation

1. Visit: `https://YOUR_USERNAME.pythonanywhere.com/swagger/`
2. You should see the Swagger UI with all API endpoints

### Test API Endpoints

**Test Listings:**
```bash
curl https://YOUR_USERNAME.pythonanywhere.com/api/listings/
```

**Test Bookings:**
```bash
curl https://YOUR_USERNAME.pythonanywhere.com/api/bookings/
```

**Test Payment Initiation:**
```bash
curl -X POST https://YOUR_USERNAME.pythonanywhere.com/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "booking-uuid-here",
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "0911234567"
  }'
```

### Test Email Notification

1. Make a payment through the API
2. Verify the payment
3. Check that email is sent (check your inbox)
4. Check Celery worker logs in the Bash console

### Test Admin Panel

1. Visit: `https://YOUR_USERNAME.pythonanywhere.com/admin/`
2. Log in with superuser credentials
3. Verify all models are accessible

---

## Troubleshooting

### Error: "502 Bad Gateway"

- Check **Error log** on Web tab
- Ensure virtual environment path is correct
- Verify WSGI file has correct username

### Error: "ModuleNotFoundError"

- Activate venv and reinstall requirements:
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt -r requirements-prod.txt
  ```

### Database Connection Error

- Verify database credentials in `.env`
- Check Database tab for correct host and port
- Ensure `mysqlclient` is installed

### Static Files Not Loading

- Run `python manage.py collectstatic`
- Check static files mapping on Web tab
- Verify `STATIC_ROOT` in settings.py

### Celery Not Running

- Check CloudAMQP URL is correct
- Verify RabbitMQ instance is active on CloudAMQP
- Check Celery worker logs in Bash console

### Email Not Sending

- Verify Gmail App Password is correct
- Check EMAIL_HOST_USER has your correct email
- Look for errors in Celery worker output

---

## Production Checklist

Before going live, ensure:

- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` set to your domain
- [ ] Database password is strong
- [ ] Gmail App Password is set (not regular password)
- [ ] Chapa API keys are production keys
- [ ] CloudAMQP instance is running
- [ ] All migrations are run
- [ ] Static files are collected
- [ ] Superuser account created
- [ ] Swagger documentation accessible at `/swagger/`
- [ ] All API endpoints tested
- [ ] Email notifications tested
- [ ] Payment flow tested

---

## URLs for Submission

After deployment, submit these URLs:

- **Main Application**: `https://YOUR_USERNAME.pythonanywhere.com/`
- **Swagger Documentation**: `https://YOUR_USERNAME.pythonanywhere.com/swagger/`
- **Admin Panel**: `https://YOUR_USERNAME.pythonanywhere.com/admin/`
- **API Root**: `https://YOUR_USERNAME.pythonanywhere.com/api/`

---

## Support

For issues with:
- **PythonAnywhere**: https://help.pythonanywhere.com/
- **CloudAMQP**: https://www.cloudamqp.com/support.html
- **Chapa**: https://developer.chapa.co/docs

---

## Notes

- Free tier PythonAnywhere has CPU limitations
- Celery workers may need to restart periodically
- CloudAMQP free tier has connection limits
- Consider upgrading for production use
