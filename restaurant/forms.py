from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Burger, Feedback, UserProfile


class BurgerForm(forms.ModelForm):
    """Form for adding/editing burgers in the admin panel."""
    class Meta:
        model = Burger
        fields = ['name', 'description', 'price', 'image_url', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/burger.jpg'}),
        }


class RegistrationForm(UserCreationForm):
    """
    Secure registration form.
    Inherits UserCreationForm which enforces AUTH_PASSWORD_VALIDATORS
    defined in settings.py (min length 8, no common passwords, etc.)
    """
    email = forms.EmailField(required=True, label='Email Address')
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Auto-create an empty UserProfile for every new user
            UserProfile.objects.get_or_create(user=user)
        return user


class SecureLoginForm(AuthenticationForm):
    """
    Wraps Django's built-in AuthenticationForm.
    Uses authenticate() internally — no raw SQL, safe against injection.
    """
    pass


class FeedbackForm(forms.ModelForm):
    """
    Feedback / contact form.
    Django ModelForm validates field types and lengths automatically.
    The message field is NOT marked | safe in templates, so XSS is prevented
    by Django's auto-escaping.
    """
    class Meta:
        model = Feedback
        fields = ['name', 'message', 'rating']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Write your feedback here...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or not (1 <= rating <= 5):
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Please enter your name.')
        return name


class UserProfileForm(forms.ModelForm):
    """Form to update the logged-in user's own profile."""
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
