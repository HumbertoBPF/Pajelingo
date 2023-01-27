from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _

class FormPicture(forms.Form):
    """Form to update profile picture"""
    picture = forms.ImageField(label='Change profile picture', required=False)

class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": "form-control",
                "placeholder": "Your email address"
            }
        ),
    )

class SetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "form-control",
                "placeholder": "New password"
            }
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": "form-control",
                "placeholder": "Confirm password"
            }
        ),
    )
