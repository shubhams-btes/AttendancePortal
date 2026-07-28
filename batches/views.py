from django.contrib.auth.mixins import LoginRequiredMixin
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