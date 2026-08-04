from django import forms

from .models import Student

from batches.models import Batch


class StudentRegistrationForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            "batch",
            "first_name",
            "last_name",
            "registration_ID",
            "email",
            "phone",
            "address",
            "degree",
            "photo",
        ]

        widgets = {

            "batch": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First Name"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last Name"
                }
            ),
            "registration_ID": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Registration ID"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Complete Address"
                }
            ),

            "degree": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "capture": "user"
                }
            ),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["batch"].queryset = Batch.objects.filter(
            is_registration_open=True,
            
            status__in=[Batch.Status.ACTIVE, Batch.Status.UPCOMING]
        ).order_by("batch_code")


class StudentUpdateForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            "batch",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "degree",
            "status",
        ]

        widgets = {

            "batch": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "degree": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

        }


class StudentSearchForm(forms.Form):

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search Name / Email / Phone"
            }
        )
    )

    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all().order_by("batch_code"),
        required=False,
        empty_label="All Batches",
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )

    status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Status"),
            ("PENDING", "Pending"),
            ("ACTIVE", "Active"),
            ("INACTIVE", "Inactive"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select"
            }
        )
    )