from django.db import models
from accounts.models import CustomUser

class Course(models.Model):

    course_name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    duration_weeks = models.PositiveIntegerField(default=24)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["course_name"]

    def __str__(self):
        return self.course_name
    
    
class Batch(models.Model):

    class Status(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    batch_code = models.CharField(
        max_length=50,
        unique=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="batches"
    )

    trainer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "TRAINER"},
        related_name="batches"
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_registration_open = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.batch_code
    
    @property
    def effective_status(self):
        """
        Status accounting for dates, so behavior is correct even if the
        admin hasn't pressed 'Refresh Status' yet. COMPLETED is always
        manual and wins over any date logic.
        """
        from django.utils import timezone

        if self.status == self.Status.COMPLETED:
            return self.Status.COMPLETED

        today = timezone.now().date()

        if self.status == self.Status.UPCOMING and self.start_date <= today:
            return self.Status.ACTIVE

        return self.status