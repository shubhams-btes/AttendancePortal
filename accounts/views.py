from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)

from .forms import LoginForm, TrainerCreationForm, TrainerUpdateForm,ProfileUpdateForm
from .models import CustomUser
from django.contrib import messages
from django.views.generic import UpdateView
from django.db.models import Q

class AdminRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role == CustomUser.Role.ADMIN
        )
        
class CustomLoginView(LoginView):

    authentication_form = LoginForm

    template_name = "accounts/login.html"

    redirect_authenticated_user = True

    def get_success_url(self):

        return reverse_lazy("dashboard:dashboard")
    
class CustomLogoutView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("accounts:login")
    
class ProfileView(LoginRequiredMixin, UpdateView):

    model = CustomUser

    form_class = ProfileUpdateForm

    template_name = "accounts/profile.html"

    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):

        messages.success(
            self.request,
            "Profile updated successfully."
        )

        return super().form_valid(form)
    
class TrainerListView(LoginRequiredMixin, AdminRequiredMixin, ListView):

    model = CustomUser

    template_name = "accounts/trainer_list.html"

    context_object_name = "trainers"

    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.filter(
            role=CustomUser.Role.TRAINER
        )

        search = self.request.GET.get("search")

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )

        status = self.request.GET.get("status")

        if status:
            queryset = queryset.filter(is_active=bool(int(status)))

        return queryset.order_by("first_name")
        
class TrainerCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):

    model = CustomUser

    form_class = TrainerCreationForm

    template_name = "accounts/trainer_form.html"

    success_url = reverse_lazy("accounts:trainer_list")
    
    def form_valid(self, form):

        form.instance.role = CustomUser.Role.TRAINER

        return super().form_valid(form)
    
class TrainerDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):

    model = CustomUser

    template_name = "accounts/trainer_detail.html"

    context_object_name = "trainer"
    
class TrainerUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):

    model = CustomUser

    form_class = TrainerUpdateForm

    template_name = "accounts/trainer_form.html"

    success_url = reverse_lazy("accounts:trainer_list")
    
class TrainerDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):

    model = CustomUser

    template_name = "accounts/trainer_confirm_delete.html"

    success_url = reverse_lazy("accounts:trainer_list")