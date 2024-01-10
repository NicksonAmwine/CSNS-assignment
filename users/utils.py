import random
from django.core.mail import send_mail
from .models import OTP
from django.contrib.auth.models import User


def generate_and_send_otp(user):
    # Generate a 6-digit OTP.
    otp = ''.join(random.choice('1234567890') for _ in range(6))

    # Save the OTP in the database.
    OTP.objects.update_or_create(user=user, defaults={'code': otp})

    # Send the OTP to the user's email.
    subject = 'One-Time Password'
    message = f'Your one-time password for logging in: {otp}'
    from_email = 'your@example.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

