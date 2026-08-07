from django import forms
from batches.models import Batch


class OOForm(forms.Form):
    # "all" is a sentinel for "all my batches"; otherwise a specific batch id
    batch = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-select"}))
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Reason (e.g. Out of office)"}),
    )

    def __init__(self, *args, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope batch choices to THIS trainer's batches, plus an "all" option.
        qs = Batch.objects.filter(trainer=trainer) if trainer else Batch.objects.none()
        choices = [("all", "All My Batches")] + [(str(b.id), b.batch_code) for b in qs]
        self.fields["batch"].choices = choices

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end:
            if end < start:
                raise forms.ValidationError("End date cannot be before start date.")
            if (end - start).days > 90:
                raise forms.ValidationError("OO range cannot exceed 90 days.")
        return cleaned
    
class HolidayForm(forms.Form):
    """Single global holiday add."""
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Republic Day"}),
    )


class HolidayCSVForm(forms.Form):
    """Bulk holiday upload."""
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".csv"}))