''' AutoChess Server Auth Forms '''

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validatiors import RegexValidator
from django.contrib.auth.models import User

class LoginForm(forms.Form):
	username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Username", 'class': 'form-control'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Password", 'class': "form-control"}))

class SignupForm(UserCreationForm):
	username = forms.CharField(label='Player Username', max_length=200, validatiors=[RegexValidator(regex='^[a-zA-Z0-9_-]*$', message='Invalid Username')] ,widget=forms.TextInput(attrs={'placeholder': "Username", 'class': 'form-control'}))
	email = forms.EmailField(widget=forms.EmailField(attrs={'placeholder': "Email", 'class': 'form-control'}))
	password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Password", 'class': 'form-control'}))
	passwordConfirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Confirm Password", 'class': 'form-control'}))

	class Meta:
		mode = User
		fields = ('username', 'email', 'password', 'passwordConfirm')