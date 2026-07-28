from django.urls import path

from .views import (
    ReportsHomeView,
    DailyAttendanceView,
    MonthlyAttendanceView,
    BatchAttendanceView,
    StudentHistoryView,
)

app_name = "reports"

urlpatterns = [

    path(
        "",
        ReportsHomeView.as_view(),
        name="reports_home",
    ),

    path(
        "daily/",
        DailyAttendanceView.as_view(),
        name="daily",
    ),

    path(
        "monthly/",
        MonthlyAttendanceView.as_view(),
        name="monthly",
    ),

    path(
        "batch/",
        BatchAttendanceView.as_view(),
        name="batch",
    ),

    path(
        "student/",
        StudentHistoryView.as_view(),
        name="student",
    ),

]