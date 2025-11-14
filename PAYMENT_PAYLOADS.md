# Payment API Payloads Reference

This document shows all request and response payloads for the payment flow.

---

## 1. Initiate Payment

### Endpoint
```
POST /api/payments/initiate/
```

### Request Payload
```json
{
  "booking_id": "f367ddf9-f2ff-4de2-b929-0e0942ace93b",
  "email": "customer@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "0911234567"
}
```

### Success Response (201 Created)
```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "checkout_url": "https://checkout.chapa.co/checkout/payment/AfjfjGjrGrj",
    "payment_id": "e6e342d2-edba-4816-9e32-30fd39b5ae4c",
    "transaction_reference": "tx-a1b2c3d4e5f6-f367ddf9-f2ff-4de2"
  }
}
```

### Error Response - Missing booking_id (400 Bad Request)
```json
{
  "status": "error",
  "message": "booking_id is required"
}
```

### Error Response - Booking Not Found (404 Not Found)
```json
{
  "status": "error",
  "message": "Booking not found"
}
```

### Error Response - Payment Already Completed (400 Bad Request)
```json
{
  "status": "error",
  "message": "Payment already completed for this booking"
}
```

### Error Response - Chapa API Error (400 Bad Request)
```json
{
  "status": "error",
  "message": "Failed to initiate payment with Chapa",
  "details": "Invalid API Key or the business can't accept payments at the moment. Please verify your API key and ensure the account is active and able to process payments."
}
```

---

## 2. Verify Payment

### Endpoint
```
GET /api/payments/verify/?tx_ref=<transaction_reference>
POST /api/payments/verify/?tx_ref=<transaction_reference>
```

### Query Parameters
- `tx_ref` (required): Transaction reference from Chapa

### Example URL
```
GET /api/payments/verify/?tx_ref=tx-a1b2c3d4e5f6-f367ddf9-f2ff-4de2
```

### Success Response - Payment Completed (200 OK)
```json
{
  "status": "success",
  "message": "Payment verified and completed successfully",
  "data": {
    "payment_id": "0da607cb-53ff-4538-9641-83d108716c19",
    "booking_id": "f367ddf9-f2ff-4de2-b929-0e0942ace93b",
    "transaction_id": "CHAPA-TEST-FFDDCD12",
    "amount": 2304.0,
    "currency": "ETB",
    "payment_status": "completed",
    "payment_method": "card",
    "payment_date": "2025-11-13T21:12:56.838672+00:00",
    "booking_status": "confirmed",
    "booking_details": {
      "property": "Spacious Family Home in New York",
      "location": "Tokyo, Japan",
      "check_in": "2026-01-15",
      "check_out": "2026-01-21",
      "guests": 1,
      "total_price": 2304.0
    },
    "customer": {
      "name": "john_doe",
      "email": "customer@example.com"
    }
  }
}
```

### Success Response - Already Verified (200 OK)
```json
{
  "status": "success",
  "message": "Payment already verified",
  "data": {
    "payment_id": "0da607cb-53ff-4538-9641-83d108716c19",
    "booking_id": "f367ddf9-f2ff-4de2-b929-0e0942ace93b",
    "payment_status": "completed",
    "amount": "2304.00",
    "transaction_id": "CHAPA-TEST-FFDDCD12"
  }
}
```

### Error Response - Missing tx_ref (400 Bad Request)
```json
{
  "status": "error",
  "message": "tx_ref is required"
}
```

### Error Response - Payment Not Found (404 Not Found)
```json
{
  "status": "error",
  "message": "Payment not found"
}
```

### Error Response - Payment Failed (400 Bad Request)
```json
{
  "status": "error",
  "message": "Payment failed or was cancelled",
  "data": {
    "payment_id": "e6e342d2-edba-4816-9e32-30fd39b5ae4c",
    "payment_status": "failed"
  }
}
```

---

## 3. Chapa Callback Payloads

### What Chapa Sends to Your Callback URL

When a customer completes payment on Chapa, they redirect to:
```
https://YOUR_DOMAIN/api/payments/verify/?tx_ref=<transaction_reference>&status=success
```

### Chapa Verification Response (from Chapa API)

When you verify with Chapa API, they return:

**Success:**
```json
{
  "status": "success",
  "message": "Transaction verified successfully",
  "data": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "customer@example.com",
    "currency": "ETB",
    "amount": "2304.00",
    "charge": "69.12",
    "mode": "test",
    "method": "card",
    "type": "API",
    "status": "success",
    "reference": "CHAPA-TEST-FFDDCD12",
    "tx_ref": "tx-a1b2c3d4e5f6-f367ddf9-f2ff-4de2",
    "customization": {
      "title": "Payment for Booking f367ddf9-f2ff-4de2",
      "description": "Payment for Spacious Family Home in New York"
    },
    "created_at": "2025-11-13T21:12:56.000000Z",
    "updated_at": "2025-11-13T21:15:23.000000Z"
  }
}
```

**Failed:**
```json
{
  "status": "failed",
  "message": "Transaction failed",
  "data": {
    "status": "failed",
    "tx_ref": "tx-a1b2c3d4e5f6-f367ddf9-f2ff-4de2"
  }
}
```

---

## 4. Email Notification Payload

After successful payment verification, an email is sent automatically.

### Email Details

**Subject:**
```
Payment Confirmation - Booking #f367ddf9
```

**From:**
```
noreply@travelapp.com
```

**To:**
```
customer@example.com
```

**Content:**
```
Dear John Doe,

Your payment has been confirmed successfully!

Booking Details:
----------------
Booking ID: f367ddf9-f2ff-4de2-b929-0e0942ace93b
Property: Spacious Family Home in New York
Location: Tokyo, Japan
Check-in: 2026-01-15
Check-out: 2026-01-21
Guests: 1

Payment Details:
----------------
Payment ID: 0da607cb-53ff-4538-9641-83d108716c19
Transaction ID: CHAPA-TEST-FFDDCD12
Amount: 2304.00 ETB
Status: Completed
Payment Date: 2025-11-13 21:12:56

Thank you for booking with us!

Best regards,
Travel Booking Team
```

---

## 5. Complete Payment Flow

### Step 1: Customer Initiates Payment
```
POST /api/payments/initiate/
→ Returns checkout_url
→ Customer redirects to Chapa
```

### Step 2: Customer Pays on Chapa
```
Customer enters card details on Chapa
→ Chapa processes payment
→ Chapa redirects to callback_url
```

### Step 3: Verification Callback
```
GET /api/payments/verify/?tx_ref=xxx&status=success
→ Your backend verifies with Chapa API
→ Updates payment status to 'completed'
→ Updates booking status to 'confirmed'
→ Triggers email notification (Celery task)
```

### Step 4: Email Sent
```
Celery worker picks up task
→ Sends payment confirmation email
→ Customer receives confirmation
```

---

## 6. Testing Payloads

### Test with cURL

**Initiate Payment:**
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "f367ddf9-f2ff-4de2-b929-0e0942ace93b",
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "0911234567"
  }'
```

**Verify Payment:**
```bash
curl -X GET "http://localhost:8000/api/payments/verify/?tx_ref=tx-a1b2c3d4e5f6-test"
```

### Test with Python
```python
import requests

# Initiate payment
response = requests.post(
    'http://localhost:8000/api/payments/initiate/',
    json={
        'booking_id': 'f367ddf9-f2ff-4de2-b929-0e0942ace93b',
        'email': 'customer@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '0911234567'
    }
)
print(response.json())

# Verify payment
tx_ref = response.json()['data']['transaction_reference']
response = requests.get(
    f'http://localhost:8000/api/payments/verify/?tx_ref={tx_ref}'
)
print(response.json())
```

---

## 7. Database Records

### Payment Model Fields
```python
{
    "payment_id": UUID,           # Primary key
    "booking": ForeignKey,        # Link to booking
    "amount": Decimal,            # Payment amount
    "currency": String,           # Currency code (ETB, USD, etc.)
    "transaction_id": String,     # Chapa transaction ID
    "payment_status": String,     # pending, completed, failed
    "payment_method": String,     # card, mobile, etc.
    "payment_date": DateTime,     # When payment completed
    "checkout_url": String,       # Chapa checkout URL
    "chapa_reference": String     # Unique transaction reference
}
```

### Status Flow
```
pending → completed (success)
pending → failed (failure)
completed → completed (idempotent)
```

---

## 8. Error Handling

All endpoints return consistent error format:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "details": "Technical details (optional)"
}
```

### HTTP Status Codes
- `200 OK` - Success (verification, already verified)
- `201 Created` - Success (payment initiated)
- `400 Bad Request` - Invalid input, business logic error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 9. Security Considerations

1. **API Keys**: Never expose in client-side code
2. **Callback URL**: Must use HTTPS in production
3. **Transaction Reference**: Always unique and unpredictable
4. **Idempotency**: Multiple verification calls are safe
5. **Email**: Only sent once per successful payment

---

## Summary

✅ **Payment Initiation**: Returns Chapa checkout URL
✅ **Payment Verification**: Confirms with Chapa API
✅ **Email Notification**: Automatic confirmation email
✅ **Error Handling**: Consistent error responses
✅ **Idempotency**: Safe to retry operations
✅ **Security**: API keys protected, HTTPS required

All payloads tested and working! 🚀
