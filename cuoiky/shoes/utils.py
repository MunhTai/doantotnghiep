import random
from django.core.mail import send_mail



def generate_otp():
    return str(random.randint(100000,900000))

def send_otp_email(user,code):
    subject = "Mã OTP xác thực tài khoản:"
    message= f"Chào {user.username},\nMã OTP của bạn là: {code}"
    send_mail(subject, message, 'youremail@gmail.com', [user.email])