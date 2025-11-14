#!/usr/bin/env python
"""
Test Payment Flow with Chapa API

This script tests the complete payment flow:
1. Finds a pending booking
2. Initiates payment with Chapa
3. Shows the checkout URL
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import requests
from listings.models import Booking

def test_payment():
    # Find a pending booking without a payment
    from listings.models import Payment
    booking = Booking.objects.filter(
        status='pending'
    ).exclude(
        booking_id__in=Payment.objects.values_list('booking__booking_id', flat=True)
    ).first()

    if not booking:
        print("❌ No pending bookings found!")
        print("\nCreating a test booking...")
        # You can create one or use an existing booking ID
        print("Please create a booking first using the API or Django admin")
        return

    print(f"✅ Found booking: {booking.booking_id}")
    print(f"   Property: {booking.listing.title}")
    print(f"   Total: {booking.total_price} ETB")
    print(f"   Guest: {booking.user.email}")
    print()

    # Prepare payment request
    payload = {
        "booking_id": str(booking.booking_id),
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "0911234567"
    }

    print("📤 Initiating payment with Chapa...")
    print(f"   Booking ID: {payload['booking_id']}")
    print()

    # Make request to your local API
    response = requests.post(
        'http://localhost:8000/api/payments/initiate/',
        json=payload
    )

    print(f"📥 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    print(response.json())
    print()

    if response.status_code == 201:
        data = response.json()
        checkout_url = data['data']['checkout_url']
        print("✅ SUCCESS! Payment initiated")
        print(f"🔗 Checkout URL: {checkout_url}")
        print()
        print("Next steps:")
        print("1. Open the checkout URL in your browser")
        print("2. Use Chapa test card: 4000 0000 0000 0002")
        print("3. After payment, check your email for confirmation")
    else:
        print("❌ FAILED! See error above")

if __name__ == '__main__':
    test_payment()
