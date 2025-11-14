#!/usr/bin/env python
"""
Simple script to test email sending functionality
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Send a test email to verify email configuration works"""

    subject = "Test Email from ALX Travel App"
    message = """
    Hello!

    This is a test email from your ALX Travel App deployment.

    If you're seeing this, your email configuration is working correctly! ✅

    Details:
    - Email Backend: Django SMTP
    - Host: smtp.gmail.com
    - Port: 587
    - TLS: Enabled

    Best regards,
    ALX Travel App Team
    """

    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['tavymatikiti@gmail.com']

    print("📧 Sending test email...")
    print(f"From: {from_email}")
    print(f"To: {recipient_list}")
    print(f"Subject: {subject}")
    print("-" * 50)

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
        print("📬 Check your inbox at tavymatikiti@gmail.com")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

if __name__ == "__main__":
    test_email()