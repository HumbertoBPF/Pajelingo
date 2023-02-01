from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from pajelingo.validators.validators import validate_email, ERROR_NOT_CONFIRMED_PASSWORD


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username"
            }
        )
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password"
            }
        )
    )

    def is_valid(self):
        for field in self.errors:
            self[field].field.widget.attrs['class'] += ' is-invalid'
        return super().is_valid()


class UserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "class": "form-control",
                "placeholder": "Email address"
            }
        ),
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password"
            }
        )
    )
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Username"
                }
            ),
            'password': forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Password"
                }
            )
        }


    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email, self.instance)
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)
        return password

    def clean(self):
        super().clean()
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("confirm_password", ERROR_NOT_CONFIRMED_PASSWORD)

    def is_valid(self):
        for field in self.errors:
            self[field].field.widget.attrs['class'] += ' is-invalid'
        return super().is_valid()

    def save(self, commit=True):
        user = super().save(commit)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class FormPicture(forms.Form):
    """Form to update profile picture"""
    picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
               "class": "form-control"
           }
       )
   )

    def is_valid(self):
        for field in self.errors:
            self[field].field.widget.attrs['class'] += ' is-invalid'
        return super().is_valid()


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

    def is_valid(self):
        for field in self.errors:
            self[field].field.widget.attrs['class'] += ' is-invalid'
        return super().is_valid()


class SetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": _(ERROR_NOT_CONFIRMED_PASSWORD),
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

    def is_valid(self):
        for field in self.errors:
            self[field].field.widget.attrs['class'] += ' is-invalid'
        return super().is_valid()

    def clean_new_password1(self):
        password1 = self.cleaned_data.get("new_password1")
        password_validation.validate_password(password1, self.user)
        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        return password2
