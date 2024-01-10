import random

def generate_and_send_otp(length=8, allowed_chars='1234567890'):
    # Generate a 6-digit OTP.
    otp = ''.join(random.choice(allowed_chars) for _ in range(length))
    return otp

my_otp = generate_and_send_otp()
print(my_otp)