from datetime import date
from django.utils import timezone

from .face_matcher import recognize_face
from .models import Attendance

from students.models import Student


def mark_attendance(image_path):
    """
    Process attendance from a captured image.

    Returns:
        {
            success,
            message,
            student,
            attendance
        }
    """

    result = recognize_face(image_path)

    if not result["success"]:

        return result

    student = result["student"]

    confidence = result["confidence"]

    if student.status != Student.Status.ACTIVE:

        return {

            "success": False,

            "message": "Student is not active."

        }

    today = date.today()

    if Attendance.objects.filter(

        student=student,

        attendance_date=today

    ).exists():

        return {

            "success": False,

            "message": "Attendance already marked today."

        }

    attendance = Attendance.objects.create(

        student=student,

        attendance_date=today,

        attendance_time=timezone.localtime().time(),

        confidence_score=confidence,

        status=Attendance.Status.PRESENT

    )

    return {

        "success": True,

        "message": "Attendance marked successfully.",

        "student": student,

        "attendance": attendance

    }