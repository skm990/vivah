from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile, Feedback, PremiumUser

User = get_user_model()

class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=60)

class OtpForm(forms.Form):
    otp = forms.CharField(label="OTP", max_length=6)
    password = forms.CharField(widget=forms.PasswordInput, label="Set Password")

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=60)
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'uid', 'created_at', 'updated_at', 'user_identity']
        widgets = {
            'caste': forms.Select(attrs={'class': 'select2 form-control'}),
            'phone_no': forms.TextInput(attrs={
                'maxlength': '10',
                'pattern': '\d{10}',
                'title': 'Please enter a valid 10-digit phone number',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark all other fields as required
        for field_name, field in self.fields.items():
            field.required = True
        if self.instance and getattr(self.instance.user, 'is_verified', False):
            for field in ['gender', 'religion',  'identity_proof', 'caste', 'post_by', 'father_name', 'mother_name', 'dob']:
                self.fields[field].required = False
                self.fields[field].disabled = True

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'message', 'rating']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your feedback...', 'rows': 5}),
            'rating': forms.HiddenInput(),  # We'll use JS for stars
        }

class PremiumUserForm(forms.ModelForm):
    class Meta:
        model = PremiumUser
        fields = ['amount', 'mobile', 'transaction_id', 'receipt']
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': 'Enter amount'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile number'}),
            'transaction_id': forms.TextInput(attrs={'placeholder': 'Enter transaction ID'}),
        }