from django.contrib import admin

from .models import Course, Batch


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "course_name",
        "duration_weeks",
        "created_at",
    )

    search_fields = (
        "course_name",
    )

    ordering = (
        "course_name",
    )


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):

    list_display = (
        "batch_code",
        "course",
        "trainer",
        "start_date",
        "end_date",
        "status",
        "is_registration_open",
    )

    list_filter = (
        "status",
        "is_registration_open",
        "course",
        "trainer",
    )

    search_fields = (
        "batch_code",
        "course__course_name",
        "trainer__first_name",
        "trainer__last_name",
    )

    autocomplete_fields = (
        "course",
        "trainer",
    )

    ordering = (
        "-start_date",
    )

    date_hierarchy = "start_date"