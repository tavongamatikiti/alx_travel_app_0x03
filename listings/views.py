"""
API Views for the travel booking application.
Implements ViewSets for Listing, Booking, and Review models with full CRUD operations.
"""

import os
import uuid
import requests
from datetime import datetime
from django.conf import settings
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer
from .tasks import send_payment_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing property listings.

    Provides full CRUD operations for listings:
    - list: GET /api/listings/
    - create: POST /api/listings/
    - retrieve: GET /api/listings/{id}/
    - update: PUT /api/listings/{id}/
    - partial_update: PATCH /api/listings/{id}/
    - destroy: DELETE /api/listings/{id}/

    Features:
    - Filtering by location and max_guests
    - Search by title, description, and location
    - Ordering by price_per_night and created_at
    """
    queryset = Listing.objects.all().select_related('host')
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'max_guests']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price_per_night', 'created_at']
    ordering = ['-created_at']


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.

    Provides full CRUD operations for bookings:
    - list: GET /api/bookings/
    - create: POST /api/bookings/
    - retrieve: GET /api/bookings/{id}/
    - update: PUT /api/bookings/{id}/
    - partial_update: PATCH /api/bookings/{id}/
    - destroy: DELETE /api/bookings/{id}/

    Features:
    - Filtering by status and listing
    - Search by listing title and user username
    - Ordering by created_at and check_in_date
    """
    queryset = Booking.objects.all().select_related('listing', 'user')
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'listing']
    search_fields = ['listing__title', 'user__username']
    ordering_fields = ['created_at', 'check_in_date']
    ordering = ['-created_at']


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews.

    Provides full CRUD operations for reviews:
    - list: GET /api/reviews/
    - create: POST /api/reviews/
    - retrieve: GET /api/reviews/{id}/
    - update: PUT /api/reviews/{id}/
    - partial_update: PATCH /api/reviews/{id}/
    - destroy: DELETE /api/reviews/{id}/

    Features:
    - Filtering by rating and listing
    - Search by comment and listing title
    - Ordering by rating and created_at
    """
    queryset = Review.objects.all().select_related('listing', 'user')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'listing']
    search_fields = ['comment', 'listing__title', 'user__username']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']


# Chapa Payment Integration Views

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def initiate_payment(request):
    """
    Initiate a payment transaction with Chapa.

    POST /api/payments/initiate/

    Request body:
    {
        "booking_id": "uuid-string",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "0911234567"
    }

    Response:
    {
        "status": "success",
        "message": "Payment initiated successfully",
        "data": {
            "checkout_url": "https://checkout.chapa.co/...",
            "payment_id": "uuid-string",
            "transaction_reference": "unique-ref"
        }
    }
    """
    try:
        # Get booking
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response(
                {"status": "error", "message": "booking_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"status": "error", "message": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if payment already exists for this booking
        existing_payment = Payment.objects.filter(
            booking=booking,
            payment_status__in=['pending', 'completed']
        ).first()

        if existing_payment:
            if existing_payment.payment_status == 'completed':
                return Response(
                    {
                        "status": "error",
                        "message": "Payment already completed for this booking"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif existing_payment.checkout_url:
                return Response(
                    {
                        "status": "success",
                        "message": "Payment already initiated",
                        "data": {
                            "checkout_url": existing_payment.checkout_url,
                            "payment_id": str(existing_payment.payment_id),
                            "transaction_reference": existing_payment.chapa_reference
                        }
                    },
                    status=status.HTTP_200_OK
                )

        # Generate unique transaction reference (max 50 chars for Chapa)
        tx_ref = f"tx-{uuid.uuid4().hex[:12]}-{str(booking_id)[:8]}"

        # Prepare Chapa payment data
        chapa_data = {
            "amount": str(booking.total_price),
            "currency": "ETB",
            "email": request.data.get('email', booking.user.email),
            "first_name": request.data.get('first_name', booking.user.first_name or booking.user.username),
            "last_name": request.data.get('last_name', booking.user.last_name or 'User'),
            "phone_number": request.data.get('phone_number', ''),
            "tx_ref": tx_ref,
            "callback_url": os.getenv('CHAPA_CALLBACK_URL', 'http://localhost:8000/api/payments/verify/'),
            "return_url": request.data.get('return_url', 'http://localhost:8000/bookings'),
            "customization": {
                "title": "Booking Payment",  # Max 16 characters
                "description": f"Payment for {booking.listing.title}"
            }
        }

        # Make request to Chapa API
        chapa_url = f"{os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
            "Content-Type": "application/json"
        }

        response = requests.post(chapa_url, json=chapa_data, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == 'success':
            # Create or update payment record
            payment, created = Payment.objects.update_or_create(
                booking=booking,
                chapa_reference=tx_ref,
                defaults={
                    'amount': booking.total_price,
                    'currency': 'ETB',
                    'payment_status': 'pending',
                    'checkout_url': response_data['data']['checkout_url']
                }
            )

            return Response(
                {
                    "status": "success",
                    "message": "Payment initiated successfully",
                    "data": {
                        "checkout_url": response_data['data']['checkout_url'],
                        "payment_id": str(payment.payment_id),
                        "transaction_reference": tx_ref
                    }
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to initiate payment with Chapa",
                    "details": response_data.get('message', 'Unknown error')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": "An error occurred",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def verify_payment(request):
    """
    Verify a payment transaction with Chapa.

    GET/POST /api/payments/verify/?tx_ref=<transaction_reference>

    Query parameters:
    - tx_ref: Transaction reference from Chapa

    Response:
    {
        "status": "success",
        "message": "Payment verified successfully",
        "data": {
            "payment_id": "uuid-string",
            "booking_id": "uuid-string",
            "payment_status": "completed",
            "amount": "1000.00",
            "transaction_id": "chapa-tx-id"
        }
    }
    """
    try:
        # Get transaction reference from query params
        # Chapa sends 'trx_ref' in webhook callback but we use 'tx_ref' in our system
        tx_ref = (request.query_params.get('tx_ref') or
                  request.query_params.get('trx_ref') or
                  request.GET.get('tx_ref') or
                  request.GET.get('trx_ref'))

        if not tx_ref:
            return Response(
                {"status": "error", "message": "tx_ref is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find payment by reference
        try:
            payment = Payment.objects.get(chapa_reference=tx_ref)
        except Payment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # If already completed, return success
        if payment.payment_status == 'completed':
            return Response(
                {
                    "status": "success",
                    "message": "Payment already verified",
                    "data": {
                        "payment_id": str(payment.payment_id),
                        "booking_id": str(payment.booking.booking_id),
                        "payment_status": payment.payment_status,
                        "amount": str(payment.amount),
                        "transaction_id": payment.transaction_id
                    }
                },
                status=status.HTTP_200_OK
            )

        # Verify with Chapa API
        chapa_url = f"{os.getenv('CHAPA_BASE_URL', 'https://api.chapa.co/v1')}/transaction/verify/{tx_ref}"
        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
        }

        response = requests.get(chapa_url, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == 'success':
            chapa_status = response_data['data']['status']

            # Update payment based on Chapa response
            if chapa_status == 'success':
                payment.payment_status = 'completed'
                payment.transaction_id = response_data['data'].get('reference')
                payment.payment_method = response_data['data'].get('payment_method', 'Unknown')
                payment.payment_date = datetime.now()
                payment.save()

                # Update booking status
                payment.booking.status = 'confirmed'
                payment.booking.save()

                # Send confirmation email asynchronously
                try:
                    send_payment_confirmation_email.delay(
                        str(payment.payment_id),
                        str(payment.booking.booking_id)
                    )
                except Exception as email_error:
                    print(f"Failed to queue email: {email_error}")

                return Response(
                    {
                        "status": "success",
                        "message": "Payment verified and completed successfully",
                        "data": {
                            "payment_id": str(payment.payment_id),
                            "booking_id": str(payment.booking.booking_id),
                            "payment_status": payment.payment_status,
                            "amount": str(payment.amount),
                            "transaction_id": payment.transaction_id
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                payment.payment_status = 'failed'
                payment.save()

                return Response(
                    {
                        "status": "error",
                        "message": "Payment failed",
                        "data": {
                            "payment_id": str(payment.payment_id),
                            "payment_status": payment.payment_status
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Failed to verify payment with Chapa",
                    "details": response_data.get('message', 'Unknown error')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": "An error occurred",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
