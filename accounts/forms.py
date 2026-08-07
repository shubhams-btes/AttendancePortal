from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)

from .models import CustomUser


class LoginForm(AuthenticationForm):
    """
    Login form for Admin and Trainer users.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
                "autofocus": True,
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        )
    )


class TrainerCreationForm(UserCreationForm):
    """
    Form used by Admin to create Trainers.
    """

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "avatar",
            "is_active",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.TRAINER

        if commit:
            user.save()

        return user


class TrainerUpdateForm(UserChangeForm):
    """
    Form used by Admin to update Trainer information.
    """

    password = None

    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "avatar",
            "is_active",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        
class ProfileUpdateForm(forms.ModelForm):

    class Meta:

        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "avatar",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }