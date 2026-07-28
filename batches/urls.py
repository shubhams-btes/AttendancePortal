from django.urls import path

from .views import (
    CourseListView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    BatchListView,
    BatchDetailView,
    BatchCreateView,
    BatchUpdateView,
    BatchDeleteView,
)

app_name = "batches"

urlpatterns = [

    # ==========================
    # Courses
    # ==========================

    path(
        "courses/",
        CourseListView.as_view(),
        name="course_list",
    ),

    path(
        "courses/add/",
        CourseCreateView.as_view(),
        name="course_add",
    ),

    path(
        "courses/<int:pk>/edit/",
        CourseUpdateView.as_view(),
        name="course_edit",
    ),

    path(
        "courses/<int:pk>/delete/",
        CourseDeleteView.as_view(),
        name="course_delete",
    ),

    # ==========================
    # Batches
    # ==========================

    path(
        "",
        BatchListView.as_view(),
        name="batch_list",
    ),

    path(
        "add/",
        BatchCreateView.as_view(),
        name="batch_add",
    ),

    path(
        "<int:pk>/",
        BatchDetailView.as_view(),
        name="batch_detail",
    ),

    path(
        "<int:pk>/edit/",
        BatchUpdateView.as_view(),
        name="batch_edit",
    ),

    path(
        "<int:pk>/delete/",
        BatchDeleteView.as_view(),
        name="batch_delete",
    ),
]