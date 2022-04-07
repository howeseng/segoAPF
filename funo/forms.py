from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms


#import django default user model
from django.contrib.auth.models import User 

from .models import Support,Profile

class CreateUserForm(UserCreationForm):
	company=forms.CharField(max_length=30, required=True)
	
	class Meta: 
		model = User	
		fields = ('username', 'email','password1', 'password2',)

class SupportForm(ModelForm):
	
	class Meta:
		model = Support
		fields = '__all__'


class UpdateProfileForm(ModelForm):
	
	class Meta:
		model=Profile
		fields=('first_name','last_name','email','company','address','city','country','postalcode')
		