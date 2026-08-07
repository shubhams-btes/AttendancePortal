from django.db import models
from students.models import Student
from batches.models import Batch
from accounts.models import CustomUser

class Attendance(models.Model):

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        LEAVE = "LEAVE", "Leave"
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

    reason = models.CharField(max_length=200, null=True, blank=True)  # for LEAVE rows
    
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
    
from batches.models import Batch
from accounts.models import CustomUser

class Holiday(models.Model):

    class Type(models.TextChoices):
        HOLIDAY = "HOLIDAY", "Holiday"       # global / admin-declared
        OO = "OO", "Out of Office"            # trainer leave

    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.HOLIDAY,
    )

    start_date = models.DateField()

    end_date = models.DateField(null=True, blank=True)   # null → single day

    reason = models.CharField(max_length=200)

    batch = models.ForeignKey(
        Batch,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="holidays",
    )
    # batch = NULL → global holiday (all batches)
    # batch set    → OO for that specific batch

    created_by = models.ForeignKey(
        CustomUser,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_holidays",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["batch"]),
        ]

    def __str__(self):
        scope = self.batch.batch_code if self.batch else "Global"
        return f"{self.get_type_display()} — {scope} ({self.start_date})"