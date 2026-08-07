from django.db import models
from batches.models import Batch


class Student(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name="students"
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)
    
    registration_ID = models.CharField(max_length=100,null=True,blank=True)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15, unique=True)

    address = models.TextField(blank=True, null=True)

    DEGREE_CHOICES = [
    ("BTECH", "B.Tech"),
    ("BCA", "BCA"),
    ("MCA", "MCA"),
    ("MTECH", "M.Tech"),
    ("MSC", "M.Sc"),
    ("OTHER", "Other"),
    ]

    degree = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        default="OTHER"
    )
    
    photo = models.ImageField(
        upload_to="students/profile_pictures/",null=True,blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    registration_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    approved_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_students"
    )

    approved_on = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["first_name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # @property
    # def registration_date(self):
    #     return self.created_at
    
    @property
    def has_attendance(self):
        return self.attendance_records.exists()
    
class FaceProfile(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="face_profile"
    )

    

    face_encoding = models.JSONField()

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student.__str__()