from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, label="Select Role")
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=True, label="Gender")
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number', 'role', 'gender')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only numbers.")
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError("Phone number must be between 10 and 15 digits.")
        return phone

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'gender')
        
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only numbers.")
        if len(phone) < 10 or len(phone) > 15:
            raise forms.ValidationError("Phone number must be between 10 and 15 digits.")
        return phone
