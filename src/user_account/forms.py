from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms import Form, fields
from django import forms
from user_account.models import User


class UserAccountRegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", 'first_name', 'last_name', 'email')

    def clean_email(self):
        if User.objects.all().filter(email=self.cleaned_data['email']).exists() and self.cleaned_data['email'] != self.initial['email']:
            raise ValidationError('Email already exists.')
        return self.cleaned_data['email']


class UserAccountProfileForm(UserChangeForm):

    class Meta(UserCreationForm.Meta):
        fields = ("username", 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.all().filter(email=email).exists() and email != self.initial['email']:
            raise ValidationError('Email already exists.')
        return email


class UserProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['image']


class ContactUs(Form):
    subject = fields.CharField(max_length=256, empty_value='Message from TestSuite')
    message = fields.CharField(widget=forms.Textarea)
