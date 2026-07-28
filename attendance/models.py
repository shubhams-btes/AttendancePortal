from django.db import models
from students.models import Student


class Attendance(models.Model):

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        LATE = "LATE", "Late"
        ABSENT = "ABSENT", "Absent"

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    attendance_date = models.DateField()

    attendance_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attendance_date", "-attendance_time"]

        constraints = [
            models.UniqueConstraint(
                fields=["student","attendance_date"],
                name="unique_student_attendance"
            )
        ]

        indexes = [
            models.Index(fields=["attendance_date"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.attendance_date}"