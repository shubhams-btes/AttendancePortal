from django.urls import path

from .views import (
    AttendanceView,
    OOListCreateView, 
    OODeleteView,
    HolidayAdminListView,
    HolidayAdminView, 
    HolidayDeleteView
)

app_name = "attendance"

urlpatterns = [

    path(
        "",
        AttendanceView.as_view(),
        name="attendance"
    ),
    path("oo/", OOListCreateView.as_view(), name="oo_manage"),
    path("oo/<int:pk>/delete/", OODeleteView.as_view(), name="oo_delete"),
    path("holiday_list/", HolidayAdminListView.as_view(), name="holiday_admin_list"),
    path("holidays/", HolidayAdminView.as_view(), name="holiday_admin"),
    path("holidays/<int:pk>/delete/", HolidayDeleteView.as_view(), name="holiday_delete"),

]