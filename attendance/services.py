from datetime import date
from django.utils import timezone

from .face_matcher import recognize_face
from .models import Attendance
from .utils import is_holiday
from students.models import Student
from django.db import IntegrityError
from batches.models import Batch

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

        return {"success": False,"message": "Student is not active."}
    
    today = date.today()

    # Block marking on weekends, holidays, or when this student's batch is OO.
    if is_holiday(today, student.batch):
        return {"success": False, "message": "Attendance is closed today (holiday / trainer OO)."}
        
    # Gate on the BATCH being active too — using effective_status so a batch
    # that started today works immediately, even if the stored field hasn't
    # been refreshed yet.
    if student.batch.effective_status != Batch.Status.ACTIVE:
        return {"success": False, "message": "Attendance is not open for this batch."}

    today = date.today()

    if Attendance.objects.filter(student=student, attendance_date=today).exists():
        return {"success": False, "message": "Attendance already marked today."}

    try:
        attendance = Attendance.objects.create(
            student=student,
            attendance_date=today,
            attendance_time=timezone.localtime().time(),
            confidence_score=confidence,
            status=Attendance.Status.PRESENT,
        )
    except IntegrityError:
        # Two rapid scans raced past the .exists() check; the unique
        # constraint caught the duplicate. Treat as already-marked.
        return {"success": False, "message": "Attendance already marked today."}

    return {
        "success": True,
        "message": "Attendance marked successfully.",
        "student": student,
        "attendance": attendance,
    }