"""
Celery tasks for the travel booking application.
Handles asynchronous operations like sending email notifications.
"""

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Payment, Booking


@shared_task
def send_payment_confirmation_email(payment_id, booking_id):
    """
    Send a payment confirmation email to the user after successful payment.

    Args:
        payment_id (str): UUID of the payment
        booking_id (str): UUID of the booking

    Returns:
        dict: Status of the email sending operation
    """
    try:
        # Retrieve payment and booking details
        payment = Payment.objects.select_related('booking', 'booking__user', 'booking__listing').get(
            payment_id=payment_id
        )
        booking = payment.booking

        # Prepare email content
        subject = f"✓ Payment Confirmed - Booking #{str(booking.booking_id)[:8]}"

        # Plain text version (fallback)
        text_content = f"""
Dear {booking.user.username},

Your payment has been confirmed successfully!

Booking Details:
----------------
Booking ID: {booking.booking_id}
Property: {booking.listing.title}
Location: {booking.listing.location}
Check-in: {booking.check_in_date}
Check-out: {booking.check_out_date}
Guests: {booking.number_of_guests}

Payment Details:
----------------
Payment ID: {payment.payment_id}
Transaction ID: {payment.transaction_id}
Amount: {payment.amount} {payment.currency}
Status: {payment.get_payment_status_display()}
Payment Date: {payment.payment_date.strftime('%Y-%m-%d %H:%M:%S') if payment.payment_date else 'N/A'}

Thank you for booking with us!

Best regards,
Travel Booking Team
"""

        # HTML version with professional styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600;">Payment Confirmed!</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">Your booking has been successfully confirmed</p>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                Dear <strong>{booking.user.username}</strong>,
                            </p>
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 15px; line-height: 1.6;">
                                Great news! Your payment has been processed successfully. We're excited to host you!
                            </p>

                            <!-- Booking Details Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8f9fa; border-radius: 6px; overflow: hidden; margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h2 style="margin: 0 0 15px 0; color: #667eea; font-size: 18px; font-weight: 600;">📍 Booking Details</h2>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Booking ID:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{str(booking.booking_id)[:8]}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Property:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{booking.listing.title}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Location:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{booking.listing.location}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Check-in:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{booking.check_in_date}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Check-out:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{booking.check_out_date}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Guests:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{booking.number_of_guests}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- Payment Details Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8f9fa; border-radius: 6px; overflow: hidden; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h2 style="margin: 0 0 15px 0; color: #28a745; font-size: 18px; font-weight: 600;">💳 Payment Details</h2>
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Transaction ID:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{payment.transaction_id}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Amount Paid:</td>
                                                <td style="color: #28a745; font-size: 18px; font-weight: 600; text-align: right; padding: 8px 0;">{payment.amount} {payment.currency}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Payment Status:</td>
                                                <td style="text-align: right; padding: 8px 0;">
                                                    <span style="background-color: #28a745; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{payment.get_payment_status_display()}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="color: #666666; font-size: 14px; padding: 8px 0;">Payment Date:</td>
                                                <td style="color: #333333; font-size: 14px; font-weight: 500; text-align: right; padding: 8px 0;">{payment.payment_date.strftime('%B %d, %Y at %H:%M') if payment.payment_date else 'N/A'}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- Call to Action -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                                <tr>
                                    <td style="text-align: center; padding: 10px 0;">
                                        <p style="margin: 0 0 15px 0; color: #666666; font-size: 14px;">Need help or have questions?</p>
                                        <a href="mailto:support@travelapp.com" style="display: inline-block; background-color: #667eea; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 6px; font-size: 14px; font-weight: 600;">Contact Support</a>
                                    </td>
                                </tr>
                            </table>

                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                Thank you for choosing us! We look forward to hosting you.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef;">
                            <p style="margin: 0 0 10px 0; color: #333333; font-size: 16px; font-weight: 600;">Travel Booking Team</p>
                            <p style="margin: 0 0 15px 0; color: #666666; font-size: 13px;">Your trusted travel companion</p>
                            <p style="margin: 0; color: #999999; font-size: 12px;">
                                This is an automated email. Please do not reply directly to this message.<br>
                                For support, contact us at <a href="mailto:support@travelapp.com" style="color: #667eea; text-decoration: none;">support@travelapp.com</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

        # Send email with both plain text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[booking.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        return {
            'status': 'success',
            'message': f'Email sent to {booking.user.email}',
            'payment_id': str(payment_id),
            'booking_id': str(booking_id)
        }

    except Payment.DoesNotExist:
        error_msg = f"Payment {payment_id} not found"
        return {
            'status': 'error',
            'message': error_msg
        }

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        return {
            'status': 'error',
            'message': error_msg
        }
