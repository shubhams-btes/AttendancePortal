from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [

    # Authentication
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login"
    ),

    path(
        "logout/",
        views.CustomLogoutView.as_view(),
        name="logout"
    ),

    # Profile
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile"
    ),

    # Trainer Management
    path(
        "trainers/",
        views.TrainerListView.as_view(),
        name="trainer_list"
    ),

    path(
        "trainers/add/",
        views.TrainerCreateView.as_view(),
        name="trainer_add"
    ),

    path(
        "trainers/<int:pk>/",
        views.TrainerDetailView.as_view(),
        name="trainer_detail"
    ),

    path(
        "trainers/<int:pk>/edit/",
        views.TrainerUpdateView.as_view(),
        name="trainer_edit"
    ),

    path(
        "trainers/<int:pk>/delete/",
        views.TrainerDeleteView.as_view(),
        name="trainer_delete"
    ),
]