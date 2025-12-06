from django import forms
from .models import Nguoidung
from django.contrib.auth.forms import UserCreationForm


class dangkyform (UserCreationForm ):
  class Meta:
    model = Nguoidung
    fields = ['username','phone','email','address','password1','password2']

  def clean_email(self):
    email = self.cleaned_data.get('email')
    if Nguoidung.objects.filter(email=email).exists():
      raise forms.ValidationError("Email này đã được sử dụng")
    return email

  def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    if Nguoidung.objects.filter(phone=phone).exists():
      raise forms.ValidationError("SĐT này đã được sử dụng")
    return phone