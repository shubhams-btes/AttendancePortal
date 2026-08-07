from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    DeleteView,
    View,
)
from django.utils import timezone
from .forms import (
    StudentRegistrationForm,
    StudentUpdateForm,
    StudentSearchForm,
    StudentLeaveForm
)
from datetime import timedelta, time
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from .models import Student
from .services import create_face_profile
from accounts.views import AdminRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.db.models import Case, When, IntegerField

from attendance.models import Attendance
from attendance.utils import is_holiday



class StudentRegistrationView(CreateView):

    model = Student

    form_class = StudentRegistrationForm

    template_name = "students/registration.html"

    success_url = reverse_lazy("students:registration_success")

    # def form_valid(self, form):

    #     with transaction.atomic():

    #         self.object = form.save()

    #         success, message = create_face_profile(self.object)

    #         if not success:

    #             self.object.delete()

    #             form.add_error(
    #                 "photo",
    #                 message
    #             )

    #             return self.form_invalid(form)

    #     messages.success(
    #         self.request,
    #         "Registration completed successfully."
    #     )

    #     return HttpResponseRedirect(
    #         self.get_success_url()
    #     )


class RegistrationSuccessView(TemplateView):

    template_name = "students/registration_success.html"


class StudentListView(LoginRequiredMixin, ListView):

    model = Student

    template_name = "students/student_list.html"

    context_object_name = "students"

    paginate_by = 15

    def get_queryset(self):

        queryset = Student.objects.select_related("batch").annotate(
            status_rank=Case(
                When(status="INACTIVE", then=2),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by("status_rank", "first_name")

        user = self.request.user

        if user.role == "TRAINER":

            queryset = queryset.filter(
                batch__trainer=user
            )

        search = self.request.GET.get("search")

        if search:

            queryset = queryset.filter(

                Q(first_name__icontains=search) |

                Q(last_name__icontains=search) |

                Q(email__icontains=search) |

                Q(phone__icontains=search)

            )

        batch = self.request.GET.get("batch")

        if batch:

            queryset = queryset.filter(batch_id=batch)

        status = self.request.GET.get("status")

        if status:

            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["search_form"] = StudentSearchForm(
            self.request.GET
        )

        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    context_object_name = "student"

    def get_queryset(self):
        qs = Student.objects.select_related("batch")
        if self.request.user.role == "TRAINER":
            return qs.filter(batch__trainer=self.request.user)
        return qs


class StudentUpdateView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    UpdateView
):

    model = Student

    form_class = StudentUpdateForm

    template_name = "students/student_form.html"

    success_url = reverse_lazy("students:student_list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Student updated successfully."
        )

        return super().form_valid(form)


class StudentDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = reverse_lazy("students:student_list")

    def post(self, request, *args, **kwargs):
        student = self.get_object()
        if student.has_attendance:
            messages.error(
                request,
                "This student has attendance records and cannot be deleted. "
                "Deactivate them instead to preserve the history."
            )
            return redirect("students:student_list")
        return super().post(request, *args, **kwargs)


class StudentActivateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "students/student_activate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = get_object_or_404(Student, pk=self.kwargs["pk"])
        return context

    def post(self, request, *args, **kwargs):
        student = get_object_or_404(Student, pk=self.kwargs["pk"])

        # Does this student already have a face profile?
        has_face = hasattr(student, "face_profile")

        if not has_face:
            # First-time approval → generate the encoding from the photo.
            success, message = create_face_profile(student)
            if not success:
                messages.error(request, f"Could not activate — {message}")
                return redirect("students:student_list")
            student.approved_by = request.user
            student.approved_on = timezone.now()

        # Both first-time and re-activation: set ACTIVE.
        student.status = Student.Status.ACTIVE
        student.save()

        if has_face:
            messages.success(request, "Student re-activated.")
        else:
            messages.success(request, "Student activated and face profile created.")
        return redirect("students:student_list")


class StudentDeactivateView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.status = Student.Status.INACTIVE
        student.save(update_fields=["status"])
        messages.success(request, "Student marked as inactive.")
        return redirect("students:student_list")
    



class MarkStudentLeaveView(LoginRequiredMixin, View):

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)

        # Server-side scope: only this student's batch trainer (or admin) may mark leave.
        user = request.user
        if user.role != "ADMIN" and student.batch.trainer_id != user.id:
            messages.error(request, "You can only mark leave for students in your own batches.")
            return redirect("batches:batch_detail", pk=student.batch_id)

        form = StudentLeaveForm(request.POST)
        if not form.is_valid():
            # Surface the first error; the form is in a modal so we redirect back.
            for err in form.errors.values():
                messages.error(request, err[0])
            return redirect("batches:batch_detail", pk=student.batch_id)

        start = form.cleaned_data["start_date"]
        end = form.cleaned_data["end_date"]
        reason = form.cleaned_data["reason"]

        # Days this student already has an attendance record for (any status),
        # so we skip them (unique constraint is per student per day).
        existing_dates = set(
            Attendance.objects.filter(
                student=student,
                attendance_date__range=(start, end),
            ).values_list("attendance_date", flat=True)
        )

        reg_date = student.registration_date.date() if student.registration_date else None

        created = 0
        skipped_weekend_holiday = 0
        skipped_existing = 0
        skipped_prereg = 0

        current = start
        while current <= end:

            # Skip weekends / holidays
            if is_holiday(current):
                skipped_weekend_holiday += 1
                current += timedelta(days=1)
                continue

            # Skip days before the student registered
            if reg_date and current < reg_date:
                skipped_prereg += 1
                current += timedelta(days=1)
                continue

            # Skip days already having an attendance record
            if current in existing_dates:
                skipped_existing += 1
                current += timedelta(days=1)
                continue

            try:
                Attendance.objects.create(
                    student=student,
                    attendance_date=current,
                    attendance_time=time(0, 0),          # leave rows: midnight placeholder
                    status=Attendance.Status.LEAVE,
                    reason=reason,
                )
                created += 1
            except IntegrityError:
                # Race: something inserted for this day between our check and now.
                skipped_existing += 1

            current += timedelta(days=1)

        # Build a clear summary of what actually happened.
        parts = [f"Leave marked for {created} day(s)."]
        skipped_total = skipped_weekend_holiday + skipped_existing + skipped_prereg
        if skipped_total:
            details = []
            if skipped_weekend_holiday:
                details.append(f"{skipped_weekend_holiday} weekend/holiday")
            if skipped_existing:
                details.append(f"{skipped_existing} already marked")
            if skipped_prereg:
                details.append(f"{skipped_prereg} before registration")
            parts.append(f"Skipped: {', '.join(details)}.")

        if created:
            messages.success(request, " ".join(parts))
        else:
            messages.warning(request, " ".join(parts) + " No leave was recorded.")

        return redirect("batches:batch_detail", pk=student.batch_id)