# Test Payment Flow - Step by Step Guide

## Prerequisites ✅
- Django server running on http://localhost:8000
- Celery worker running (for email notifications)
- Database has bookings (at least one pending booking)

---

## Quick Test (3 Steps)

### Step 1: Start Django Server

```bash
cd /Users/tavongamatikiti/Developer/alx/alx_travel_app_0x03
source venv/bin/activate
python manage.py runserver
```

Keep this terminal open.

### Step 2: Start Celery Worker (New Terminal)

```bash
cd /Users/tavongamatikiti/Developer/alx/alx_travel_app_0x03
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

Keep this terminal open too.

### Step 3: Run Test Script (New Terminal)

```bash
cd /Users/tavongamatikiti/Developer/alx/alx_travel_app_0x03
source venv/bin/activate
python test_payment.py
```

---

## Manual Test with cURL

If you already know a booking ID:

```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "YOUR_BOOKING_ID_HERE",
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "0911234567"
  }'
```

Replace `YOUR_BOOKING_ID_HERE` with an actual booking ID from your database.

---

## Get a Booking ID

```bash
python manage.py shell
```

Then in the shell:
```python
from listings.models import Booking
booking = Booking.objects.first()
print(f"Booking ID: {booking.booking_id}")
print(f"Property: {booking.listing.title}")
print(f"Total: {booking.total_price} ETB")
exit()
```

Copy the booking ID and use it in the cURL command above.

---

## Expected Results

### ✅ Success Response:
```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "checkout_url": "https://checkout.chapa.co/checkout/payment/AfjfjGjrGrj469",
    "payment_id": "e6e342d2-edba-4816-9e32-30fd39b5ae4c",
    "transaction_reference": "tx-a1b2c3d4e5f6-f367ddf9"
  }
}
```

### What Happens Next:
1. ✅ You get a Chapa checkout URL
2. 🌐 Open the URL in your browser
3. 💳 Enter test card: **4000 0000 0000 0002**
4. ✅ Complete payment on Chapa
5. 📧 Receive confirmation email at your configured email
6. ✅ Booking status changes to "confirmed"

---

## Chapa Test Cards

**Success:**
- Card: 4000 0000 0000 0002
- CVV: Any 3 digits (e.g., 123)
- Expiry: Any future date (e.g., 12/25)

**Decline:**
- Card: 4000 0000 0000 0069

---

## Troubleshooting

### Server Not Running
```bash
python manage.py runserver
```

### No Bookings Found
Create one via Django admin:
```bash
python manage.py createsuperuser  # if you don't have one
python manage.py runserver
# Then go to: http://localhost:8000/admin/
```

Or use the seed command:
```bash
python manage.py seed
```

### Email Not Sending
- Make sure Celery worker is running
- Check .env has correct Gmail credentials
- Check Celery worker terminal for errors

---

## Full Test Checklist

- [ ] Django server running (Terminal 1)
- [ ] Celery worker running (Terminal 2)
- [ ] Database has bookings
- [ ] Run test script or cURL command
- [ ] Get checkout URL
- [ ] Open URL in browser
- [ ] Enter test card details
- [ ] Complete payment
- [ ] Check email inbox
- [ ] Verify booking status changed to "confirmed"

---

## What Got Fixed

The Chapa API was rejecting our requests because the title was too long:

**Before (WRONG):**
```json
{
  "customization": {
    "title": "Payment for Booking f367ddf9-f2ff-4de2-b929-0e0942ace93b"
  }
}
```
Length: 61 characters ❌ (limit is 16)

**After (FIXED):**
```json
{
  "customization": {
    "title": "Booking Payment"
  }
}
```
Length: 15 characters ✅

Now it works!
