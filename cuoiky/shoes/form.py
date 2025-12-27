from django import forms
from .models import Nguoidung
from django.contrib.auth.forms import UserCreationForm


class dangkyform (UserCreationForm ):
  class Meta:
    model = Nguoidung
    fields = ['username','phone','email','password1','password2']



