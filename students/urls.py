from django.urls import path

from .views import (
    StudentRegistrationView,
    RegistrationSuccessView,
    StudentListView,
    StudentDetailView,
    StudentUpdateView,
    StudentDeleteView,
    StudentActivateView,
    StudentDeactivateView,
)

app_name = "students"

urlpatterns = [

    # -------------------------
    # Public Registration
    # -------------------------

    path(
        "register/",
        StudentRegistrationView.as_view(),
        name="register",
    ),

    path(
        "register/success/",
        RegistrationSuccessView.as_view(),
        name="registration_success",
    ),

    # -------------------------
    # Student Management
    # -------------------------

    path(
        "",
        StudentListView.as_view(),
        name="student_list",
    ),

    path(
        "<int:pk>/",
        StudentDetailView.as_view(),
        name="student_detail",
    ),

    path(
        "<int:pk>/edit/",
        StudentUpdateView.as_view(),
        name="student_edit",
    ),

    path(
        "<int:pk>/delete/",
        StudentDeleteView.as_view(),
        name="student_delete",
    ),

    path(
        "<int:pk>/activate/",
        StudentActivateView.as_view(),
        name="student_activate",
    ),

    path(
        "<int:pk>/deactivate/",
        StudentDeactivateView.as_view(),
        name="student_deactivate",
    ),

]