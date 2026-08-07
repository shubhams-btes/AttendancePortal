from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from accounts.models import CustomUser
from accounts.views import AdminRequiredMixin
from .forms import CourseForm, BatchForm
from .models import Course, Batch
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

def _is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"
# ==========================================================
# COURSE VIEWS
# ==========================================================

class CourseListView(LoginRequiredMixin, ListView):

    model = Course

    template_name = "batches/course_list.html"

    context_object_name = "courses"

    ordering = ["course_name"]


class CourseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):

    model = Course

    form_class = CourseForm

    template_name = "batches/course_form.html"

    success_url = reverse_lazy("batches:course_list")


class CourseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):

    model = Course

    form_class = CourseForm

    template_name = "batches/course_form.html"

    success_url = reverse_lazy("batches:course_list")


class CourseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Course
    template_name = "batches/course_confirm_delete.html"
    success_url = reverse_lazy("batches:course_list")

    def post(self, request, *args, **kwargs):
        from django.db.models import ProtectedError
        from django.contrib import messages
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "Cannot delete this course — it has batches assigned to it.")
            return redirect("batches:course_list")


# ==========================================================
# BATCH VIEWS
# ==========================================================

class BatchListView(LoginRequiredMixin, ListView):

    model = Batch

    template_name = "batches/batch_list.html"

    context_object_name = "batches"

    ordering = ["-start_date"]

    def get_queryset(self):

        if self.request.user.role == CustomUser.Role.ADMIN:
            return Batch.objects.select_related(
                "course",
                "trainer"
            )

        return Batch.objects.select_related(
            "course",
            "trainer"
        ).filter(
            trainer=self.request.user
        )


class BatchDetailView(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = "batches/batch_detail.html"
    context_object_name = "batch"

    def get_queryset(self):
        qs = Batch.objects.select_related("course", "trainer")
        if self.request.user.role == CustomUser.Role.ADMIN:
            return qs
        return qs.filter(trainer=self.request.user)


class BatchCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):

    model = Batch

    form_class = BatchForm

    template_name = "batches/batch_form.html"

    success_url = reverse_lazy("batches:batch_list")


class BatchUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):

    model = Batch

    form_class = BatchForm

    template_name = "batches/batch_form.html"

    success_url = reverse_lazy("batches:batch_list")


class BatchDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):

    model = Batch

    template_name = "batches/batch_confirm_delete.html"

    success_url = reverse_lazy("batches:batch_list")
    

@user_passes_test(_is_admin)
@require_POST
def refresh_batch_status(request):
    """
    Sync stored batch status to the current date:
    UPCOMING → ACTIVE once start_date has arrived.
    COMPLETED is left untouched (manual only).
    """
    today = timezone.now().date()

    activated = Batch.objects.filter(
        status=Batch.Status.UPCOMING,
        start_date__lte=today,
    ).update(status=Batch.Status.ACTIVE)

    if activated:
        messages.success(request, f"{activated} batch(es) activated.")
    else:
        messages.info(request, "No batches needed activation.")

    return redirect("batches:batch_list")