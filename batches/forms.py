from django import forms

from .models import Course, Batch


class CourseForm(forms.ModelForm):

    class Meta:
        model = Course

        fields = [
            "course_name",
            "description",
            "duration_weeks",
        ]

        widgets = {
            "course_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Course Name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Course Description",
                }
            ),
            "duration_weeks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }


class BatchForm(forms.ModelForm):

    class Meta:
        model = Batch

        fields = [
            "batch_code",
            "course",
            "trainer",
            "start_date",
            "end_date",
            "is_registration_open",
            "status",
        ]

        widgets = {
            "batch_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Batch Code",
                }
            ),
            "course": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "trainer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "is_registration_open": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:

            if end_date < start_date:

                raise forms.ValidationError(
                    "End date cannot be earlier than Start date."
                )

        return cleaned_data