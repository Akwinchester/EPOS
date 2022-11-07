from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class Register_User(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput())
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username','password1', 'password2')