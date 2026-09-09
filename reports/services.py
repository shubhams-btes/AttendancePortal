from datetime import date
import calendar
from attendance.models import Attendance
from students.models import Student
from batches.models import Batch
from attendance.utils import holiday_type


def build_monthly_report(user, year, month, batch_id=None):
    """Returns (report, total_days, students-scoped) — the same data the view renders."""
    students = Student.objects.select_related("batch").filter(status=Student.Status.ACTIVE)

    if user.role == "TRAINER":
        students = students.filter(batch__trainer=user)
    if batch_id:
        students = students.filter(batch_id=batch_id)

    total_days = calendar.monthrange(year, month)[1]

    attendance = Attendance.objects.filter(
        attendance_date__year=year,
        attendance_date__month=month,
        student__in=students,
    )
    attendance_map = {
        (r.student_id, r.attendance_date.day): r.status for r in attendance
    }

    today = date.today()
    report = []

    for student in students:
        row = {"student": student, "days": [], "present": 0, "leave": 0, "absent": 0, "percentage": 0}

        for day in range(1, total_days + 1):
            current_date = date(year, month, day)

            if current_date > today:
                ht = holiday_type(current_date, student.batch)
                if ht == "OO":
                    row["days"].append("OO")
                elif ht in ("WEEKEND", "HOLIDAY"):
                    row["days"].append("H")
                elif attendance_map.get((student.id, day)) == Attendance.Status.LEAVE:
                    row["days"].append("L"); row["leave"] += 1
                else:
                    row["days"].append("-")
                continue

            ht = holiday_type(current_date, student.batch)
            if ht == "OO":
                row["days"].append("OO"); continue
            if ht in ("WEEKEND", "HOLIDAY"):
                row["days"].append("H"); continue

            if student.registration_date and current_date < student.registration_date.date():
                row["days"].append("-"); continue

            att = attendance_map.get((student.id, day))
            if att == Attendance.Status.PRESENT:
                row["days"].append("P"); row["present"] += 1
            elif att == Attendance.Status.LEAVE:
                row["days"].append("L"); row["leave"] += 1
            else:
                row["days"].append("A"); row["absent"] += 1

        wd = row["present"] + row["absent"]
        if wd:
            row["percentage"] = round((row["present"] / wd) * 100, 2)
        report.append(row)

    return report, total_days


def build_monthly_workbook(report, total_days, year, month):
    """Turn the report matrix into an Excel grid."""
    import openpyxl
    from openpyxl.styles import Font, Alignment

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{calendar.month_name[month]} {year}"[:31]

    # Header: Student | 1 | 2 | ... | N | P | L | A | %
    headers = ["Student", "Batch"] + [str(d) for d in range(1, total_days + 1)] + ["P", "L", "A", "%"]
    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col, value=h)
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    for r_idx, row in enumerate(report, start=2):
        ws.cell(row=r_idx, column=1, value=f"{row['student'].first_name} {row['student'].last_name}")
        ws.cell(row=r_idx, column=2, value=row["student"].batch.batch_code)
        for d_idx, token in enumerate(row["days"], start=3):
            ws.cell(row=r_idx, column=d_idx, value=token)
        base = 3 + total_days
        ws.cell(row=r_idx, column=base,     value=row["present"])
        ws.cell(row=r_idx, column=base + 1, value=row["leave"])
        ws.cell(row=r_idx, column=base + 2, value=row["absent"])
        ws.cell(row=r_idx, column=base + 3, value=row["percentage"])

    return wb