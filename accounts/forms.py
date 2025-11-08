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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fields that should NOT be required
        not_required_fields = ['uid', 'user', 'user_identity']
        # Mark all other fields as required
        for field_name, field in self.fields.items():
            if field_name not in not_required_fields:
                field.required = True


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