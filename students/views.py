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
)

from .models import Student
from .services import create_face_profile
from accounts.views import AdminRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect

class StudentRegistrationView(CreateView):

    model = Student

    form_class = StudentRegistrationForm

    template_name = "students/registration.html"

    success_url = reverse_lazy("students:registration_success")

    def form_valid(self, form):

        with transaction.atomic():

            self.object = form.save()

            success, message = create_face_profile(self.object)

            if not success:

                self.object.delete()

                form.add_error(
                    "photo",
                    message
                )

                return self.form_invalid(form)

        messages.success(
            self.request,
            "Registration completed successfully."
        )

        return HttpResponseRedirect(
            self.get_success_url()
        )


class RegistrationSuccessView(TemplateView):

    template_name = "students/registration_success.html"


class StudentListView(LoginRequiredMixin, ListView):

    model = Student

    template_name = "students/student_list.html"

    context_object_name = "students"

    paginate_by = 15

    def get_queryset(self):

        queryset = Student.objects.select_related(
            "batch"
        ).order_by("first_name")

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


class StudentDeleteView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    DeleteView
):

    model = Student

    template_name = "students/student_confirm_delete.html"

    success_url = reverse_lazy("students:student_list")


class StudentActivateView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):

    template_name = "students/student_activate.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["student"] = Student.objects.get(pk=self.kwargs["pk"])

        return context

    def post(self, request, *args, **kwargs):

        student = Student.objects.get(pk=self.kwargs["pk"])

        student.status = Student.Status.ACTIVE

        student.approved_by = request.user

        student.approved_on = timezone.now()

        student.save()

        messages.success(
            request,
            "Student activated successfully."
        )

        return redirect("students:student_list")


class StudentDeactivateView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    View
):

    def get(self, request, pk):

        student = Student.objects.get(pk=pk)

        student.status = Student.Status.INACTIVE

        student.save()

        messages.success(
            request,
            "Student marked as inactive."
        )

        return redirect("students:student_list")