import base64
import os
import uuid
from .utils import is_holiday
import csv
import io
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from .services import mark_attendance
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.views import AdminRequiredMixin
from django.views.generic import TemplateView, ListView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Attendance
from batches.models import Batch
from .models import Holiday
from .forms import OOForm,HolidayForm, HolidayCSVForm


class AttendanceView(View):

    template_name = "attendance/attendance_home.html"

    def get(self, request):

        return render(
            request,
            self.template_name
        )

    def post(self, request):
        image_data = request.POST.get("image")
        if not image_data:
            return JsonResponse({"success": False, "message": "No image received."})

        if len(image_data) > 8 * 1024 * 1024:
            return JsonResponse({"success": False, "message": "Image too large."})

        if is_holiday():
            return JsonResponse({
                "success": False,
                "message": "Today is a holiday. Attendance cannot be marked."
            })

        image_path = None
        try:
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)

            upload_dir = os.path.join(settings.MEDIA_ROOT, "attendance")
            os.makedirs(upload_dir, exist_ok=True)

            filename = f"{uuid.uuid4().hex}.png"
            image_path = os.path.join(upload_dir, filename)

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            result = mark_attendance(image_path)

            if result["success"]:
                return JsonResponse({
                    "success": True,
                    "student": str(result["student"]),
                    "confidence": float(result["attendance"].confidence_score),  # Decimal → float for JSON
                    "message": result["message"],
                })

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

        finally:
            # Always remove the temp capture — even on exception. Honors
            # "Temporary Image Deletion" and prevents orphaned face images.
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                

class OOListCreateView(LoginRequiredMixin, View):
    """Trainer's OO page: list their OO periods + create new ones."""
    template_name = "attendance/oo_manage.html"

    def get(self, request):
        oo_periods = Holiday.objects.filter(
            type=Holiday.Type.OO,
            batch__trainer=request.user,
        ).select_related("batch").order_by("-start_date")

        return self._render(request, OOForm(trainer=request.user), oo_periods)

    def post(self, request):
        form = OOForm(request.POST, trainer=request.user)

        oo_periods = Holiday.objects.filter(
            type=Holiday.Type.OO,
            batch__trainer=request.user,
        ).select_related("batch").order_by("-start_date")

        if not form.is_valid():
            return self._render(request, form, oo_periods)

        batch_choice = form.cleaned_data["batch"]
        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]
        reason = form.cleaned_data["reason"]

        # Resolve which batches this OO applies to.
        if batch_choice == "all":
            batches = Batch.objects.filter(trainer=request.user)
        else:
            # Verify the selected batch really belongs to this trainer.
            batch = get_object_or_404(Batch, pk=batch_choice, trainer=request.user)
            batches = [batch]

        # One Holiday row per batch (batch-keyed model → "all" = many rows).
        created = 0
        for b in batches:
            Holiday.objects.create(
                type=Holiday.Type.OO,
                start_date=start,
                end_date=end,
                reason=reason,
                batch=b,
                created_by=request.user,
            )
            created += 1

        messages.success(request, f"OO marked for {created} batch(es).")
        return redirect("attendance:oo_manage")

    def _render(self, request, form, oo_periods):
        from django.shortcuts import render
        return render(request, self.template_name, {
            "form": form,
            "oo_periods": oo_periods,
        })


class OODeleteView(LoginRequiredMixin, View):
    """Delete an OO period — only the owning trainer may."""
    def post(self, request, pk):
        oo = get_object_or_404(
            Holiday,
            pk=pk,
            type=Holiday.Type.OO,
            batch__trainer=request.user,   # scope: only their own OO
        )
        oo.delete()
        messages.success(request, "OO period removed.")
        return redirect("attendance:oo_manage")
            
class HolidayAdminListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Holiday
    template_name = "attendance/holiday_admin_list.html"
    context_object_name = "holidays"
    paginate_by = 20

    def get_queryset(self):
        qs = Holiday.objects.select_related("batch", "created_by").order_by("-start_date")
        # Optional filter: ?type=OO or ?type=HOLIDAY
        htype = self.request.GET.get("type")
        if htype in ("OO", "HOLIDAY"):
            qs = qs.filter(type=htype)
        return qs

class HolidayAdminView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = "attendance/holiday_admin.html"

    def get(self, request):
        return self._render(request)

    def _render(self, request, holiday_form=None, csv_form=None):
        from django.shortcuts import render
        holidays = Holiday.objects.filter(
            type=Holiday.Type.HOLIDAY
        ).select_related("created_by").order_by("-start_date")

        return render(request, self.template_name, {
            "holidays": holidays,
            "holiday_form": holiday_form or HolidayForm(),
            "csv_form": csv_form or HolidayCSVForm(),
        })

    def post(self, request):
        action = request.POST.get("action")

        if action == "add_single":
            return self._add_single(request)
        elif action == "upload_csv":
            return self._upload_csv(request)

        messages.error(request, "Unknown action.")
        return redirect("attendance:holiday_admin")

    def _add_single(self, request):
        form = HolidayForm(request.POST)
        if not form.is_valid():
            return self._render(request, holiday_form=form)

        d = form.cleaned_data["date"]
        reason = form.cleaned_data["reason"]

        # Skip if a global holiday already exists on that date
        if Holiday.objects.filter(type=Holiday.Type.HOLIDAY, batch__isnull=True, start_date=d).exists():
            messages.warning(request, f"A holiday already exists on {d}. Skipped.")
            return redirect("attendance:holiday_admin")

        Holiday.objects.create(
            type=Holiday.Type.HOLIDAY,
            start_date=d,
            reason=reason,
            batch=None,
            created_by=request.user,
        )
        messages.success(request, f"Holiday added for {d}.")
        return redirect("attendance:holiday_admin")

    def _upload_csv(self, request):
        form = HolidayCSVForm(request.POST, request.FILES)
        if not form.is_valid():
            return self._render(request, csv_form=form)

        f = request.FILES["file"]

        # Basic guards: extension + size
        if not f.name.lower().endswith(".csv"):
            messages.error(request, "Please upload a .csv file.")
            return redirect("attendance:holiday_admin")
        if f.size > 1 * 1024 * 1024:
            messages.error(request, "File too large (max 1MB).")
            return redirect("attendance:holiday_admin")

        try:
            decoded = f.read().decode("utf-8")
        except UnicodeDecodeError:
            messages.error(request, "Could not read the file. Ensure it is UTF-8 CSV.")
            return redirect("attendance:holiday_admin")

        reader = csv.DictReader(io.StringIO(decoded))

        # Validate headers
        if not reader.fieldnames or "date" not in reader.fieldnames or "reason" not in reader.fieldnames:
            messages.error(request, "CSV must have 'date' and 'reason' columns.")
            return redirect("attendance:holiday_admin")

        # Existing global holiday dates → skip duplicates
        existing = set(
            Holiday.objects.filter(type=Holiday.Type.HOLIDAY, batch__isnull=True)
            .values_list("start_date", flat=True)
        )

        created = 0
        skipped_dupe = 0
        errors = []

        to_create = []
        seen_in_file = set()

        for i, row in enumerate(reader, start=2):  # start=2: row 1 is header
            date_str = (row.get("date") or "").strip()
            reason = (row.get("reason") or "").strip()

            if not date_str or not reason:
                errors.append(f"Row {i}: missing date or reason.")
                continue

            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"Row {i}: invalid date '{date_str}' (use YYYY-MM-DD).")
                continue

            if d in existing or d in seen_in_file:
                skipped_dupe += 1
                continue

            seen_in_file.add(d)
            to_create.append(Holiday(
                type=Holiday.Type.HOLIDAY,
                start_date=d,
                reason=reason,
                batch=None,
                created_by=request.user,
            ))

        if to_create:
            Holiday.objects.bulk_create(to_create)
            created = len(to_create)

        # Build a clear summary
        parts = [f"Imported {created} holiday(s)."]
        if skipped_dupe:
            parts.append(f"{skipped_dupe} skipped (already exist).")
        if errors:
            parts.append(f"{len(errors)} row(s) had errors.")

        if created:
            messages.success(request, " ".join(parts))
        else:
            messages.warning(request, " ".join(parts))

        # Surface first few errors so the admin can fix the file
        for e in errors[:5]:
            messages.error(request, e)

        return redirect("attendance:holiday_admin")


class HolidayDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        # Only global holidays are deletable here — NOT trainer OO.
        holiday = get_object_or_404(Holiday, pk=pk, type=Holiday.Type.HOLIDAY, batch__isnull=True)
        holiday.delete()
        messages.success(request, "Holiday deleted.")
        return redirect("attendance:holiday_admin")