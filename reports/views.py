from datetime import date,datetime
import calendar


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from attendance.models import Attendance
from students.models import Student
from batches.models import Batch
from attendance.utils import is_holiday
from attendance.utils import holiday_type


WEEKEND_DAYS = [5, 6]
class ReportsHomeView(LoginRequiredMixin, TemplateView):

    template_name = "reports/reports_home.html"


class DailyAttendanceView(LoginRequiredMixin, TemplateView):

    template_name = "reports/daily_attendance.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        date_str = self.request.GET.get("date")
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()
        

        if is_holiday(selected_date):

            context["holiday"] = True
            context["holiday_message"] = (
                "The selected date is a holiday. Attendance is not applicable."
            )

            context["selected_date"] = selected_date

            batches = Batch.objects.all()

            if self.request.user.role == "TRAINER":
                batches = batches.filter(
                    trainer=self.request.user
                )

            context["batches"] = batches
            context["selected_batch"] = self.request.GET.get("batch")

            return context

        students = Student.objects.select_related(
            "batch"
        ).filter(
            status=Student.Status.ACTIVE
        )

        batches = Batch.objects.all()

        if self.request.user.role == "TRAINER":

            batches = batches.filter(
                trainer=self.request.user
            )

            students = students.filter(
                batch__trainer=self.request.user
            )

        batch_id = self.request.GET.get("batch")

        if batch_id:

            students = students.filter(
                batch_id=batch_id
            )

        attendance_map = {

            attendance.student_id: attendance

            for attendance in Attendance.objects.filter(
                attendance_date=selected_date,
                student__in=students
            )

        }

        report = []

        present = 0

        leave = 0

        absent = 0

        for student in students:
            
            ht = holiday_type(selected_date, student.batch)

            if ht == "OO":
                report.append({"student": student, "status": "OO", "time": None, "confidence": None})
                continue
            if ht in ("WEEKEND", "HOLIDAY"):
                report.append({"student": student, "status": "H", "time": None, "confidence": None})
                continue

            record = attendance_map.get(student.id)

            if record and record.status == Attendance.Status.PRESENT:
                report.append({
                    "student": student, "status": "P",
                    "time": record.attendance_time,
                    "confidence": record.confidence_score,
                })
                present += 1

            elif record and record.status == Attendance.Status.LEAVE:
                report.append({
                    "student": student, "status": "L",
                    "time": None, "confidence": None,
                })
                leave += 1

            else:
                report.append({
                    "student": student, "status": "A",
                    "time": None, "confidence": None,
                })
                absent += 1

        total = len(report)
        counted = present + absent          # leave and OO/holiday excluded
        percentage = round((present / counted) * 100, 2) if counted else 0

        if counted:

            percentage = round(

                ((present) / counted) * 100,

                2

            )

        context["report"] = report

        context["batches"] = batches

        context["selected_date"] = selected_date

        context["selected_batch"] = batch_id

        context["total"] = total

        context["present"] = present

        context["leave"] = leave

        context["absent"] = absent

        context["percentage"] = percentage

        return context


class MonthlyAttendanceView(LoginRequiredMixin, TemplateView):

    template_name = "reports/monthly_attendance.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        today = date.today() 

        year = int(
            self.request.GET.get(
                "year",
                today.year
            )
        )

        month = int(
            self.request.GET.get(
                "month",
                today.month
            )
        )

        students = Student.objects.select_related(
            "batch"
        ).filter(
            status=Student.Status.ACTIVE
        )

        batches = Batch.objects.all()

        if self.request.user.role == "TRAINER":

            batches = batches.filter(
                trainer=self.request.user
            )

            students = students.filter(
                batch__trainer=self.request.user
            )

        batch_id = self.request.GET.get("batch")

        if batch_id:

            students = students.filter(
                batch_id=batch_id
            )

        total_days = calendar.monthrange(
            year,
            month
        )[1]

        attendance = Attendance.objects.filter(

            attendance_date__year=year,

            attendance_date__month=month,

            student__in=students

        )

        attendance_map = {}

        for record in attendance:

            attendance_map[
                (record.student_id, record.attendance_date.day)
            ] = record.status

        report = []

        for student in students:

            row = {

                "student": student,

                "days": [],

                "present": 0,

                "leave": 0,

                "absent": 0,

                "percentage": 0

            }

            today = date.today()

            for day in range(1, total_days + 1):

                current_date = date(year, month, day)

                 # Future dates
                if current_date > today:
                    ht = holiday_type(current_date, student.batch)
                    if ht == "OO":
                        row["days"].append("OO")
                    elif ht in ("WEEKEND", "HOLIDAY"):
                        row["days"].append("H")
                    # Future: blank UNLESS leave was pre-marked for this day
                    elif attendance_map.get((student.id, day)) == Attendance.Status.LEAVE:
                        row["days"].append("L")
                        row["leave"] += 1
                    else:
                        row["days"].append("-")
                    continue

                # Sunday
                ht = holiday_type(current_date, student.batch)

                if ht == "OO":
                    row["days"].append("OO")
                    continue

                if ht in ("WEEKEND", "HOLIDAY"):
                    row["days"].append("H")
                    continue

                # Before student registration
                if student.registration_date:

                    if current_date < student.registration_date.date():

                        row["days"].append("-")

                        continue

                attendance = attendance_map.get((student.id, day))

                if attendance == Attendance.Status.PRESENT:
                    row["days"].append("P")
                    row["present"] += 1

                elif attendance == Attendance.Status.LEAVE:
                    row["days"].append("L")
                    row["leave"] += 1

                else:
                    row["days"].append("A")
                    row["absent"] += 1

            working_days = row["present"] + row["absent"]

            if working_days:

                row["percentage"] = round(

                    ((row["present"]) / working_days) * 100,

                    2

                )

            report.append(row)
            
        total_absent = sum(row["absent"] for row in report)
        total_working = sum(row["present"] + row["absent"] for row in report)

        absenteeism_rate = 0
        if total_working:
            absenteeism_rate = round((total_absent / total_working) * 100, 2)

        context["total_absent"] = total_absent
        context["total_working"] = total_working
        context["absenteeism_rate"] = absenteeism_rate

        context["report"] = report

        context["days"] = range(
            1,
            total_days + 1
        )

        context["month"] = month

        context["year"] = year

        context["batches"] = batches

        context["selected_batch"] = batch_id
        
        context["months"] = [

            {"value": 1, "name": "January"},
            {"value": 2, "name": "February"},
            {"value": 3, "name": "March"},
            {"value": 4, "name": "April"},
            {"value": 5, "name": "May"},
            {"value": 6, "name": "June"},
            {"value": 7, "name": "July"},
            {"value": 8, "name": "August"},
            {"value": 9, "name": "September"},
            {"value": 10, "name": "October"},
            {"value": 11, "name": "November"},
            {"value": 12, "name": "December"},

        ]

        return context


class BatchAttendanceView(LoginRequiredMixin, TemplateView):

    template_name = "reports/batch_attendance.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        date_str = self.request.GET.get("date")
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()

        if is_holiday(selected_date):

            context["holiday"] = True
            context["holiday_message"] = (
                "The selected date is a holiday. Attendance is not applicable."
            )

            context["selected_date"] = selected_date

            batches = Batch.objects.all()

            if self.request.user.role == "TRAINER":
                batches = batches.filter(
                    trainer=self.request.user
                )

            context["batches"] = batches
            context["selected_batch"] = self.request.GET.get("batch")

            return context

        batches = Batch.objects.all()

        if self.request.user.role == "TRAINER":

            batches = batches.filter(
                trainer=self.request.user
            )

        selected_batch_id = self.request.GET.get("batch")
        selected_batch = None
        if selected_batch_id:
            selected_batch = Batch.objects.filter(pk=selected_batch_id).first()

        ht = holiday_type(selected_date, selected_batch)
        
        report = []

        total = 0

        present = 0

        leave = 0

        absent = 0

        if selected_batch:

            students = Student.objects.select_related(
                "batch"
            ).filter(
                batch_id=selected_batch,
                status=Student.Status.ACTIVE
            )

            attendance_map = {

                attendance.student_id: attendance

                for attendance in Attendance.objects.filter(
                    attendance_date=selected_date,
                    student__in=students
                )

            }

            for student in students:
                
                if ht == "OO":
                    report.append({"student": student, "status": "OO", "time": None, "confidence": None})
                    continue
                if ht in ("WEEKEND", "HOLIDAY"):
                    report.append({"student": student, "status": "H", "time": None, "confidence": None})
                    continue
                record = attendance_map.get(student.id)

                if record and record.status == Attendance.Status.PRESENT:
                    report.append({
                        "student": student, "status": "P",
                        "time": record.attendance_time,
                        "confidence": record.confidence_score,
                    })
                    present += 1

                elif record and record.status == Attendance.Status.LEAVE:
                    report.append({
                        "student": student, "status": "L",
                        "time": None, "confidence": None,
                    })
                    leave += 1
                else:
                    report.append({
                        "student": student, "status": "A",
                        "time": None, "confidence": None,
                    })
                    absent += 1


        total = len(report)
        counted = present + absent
        percentage = round((present / counted) * 100, 2) if counted else 0

        if counted:

            percentage = round(

                ((present) / counted) * 100,

                2

            )

        context["batches"] = batches

        context["selected_batch"] = selected_batch

        context["selected_date"] = selected_date

        context["report"] = report

        context["total"] = total

        context["present"] = present

        context["leave"] = leave

        context["absent"] = absent

        context["percentage"] = percentage

        return context


class StudentHistoryView(LoginRequiredMixin, TemplateView):

    template_name = "reports/student_history.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        students = Student.objects.select_related(
            "batch"
        ).filter(
            status=Student.Status.ACTIVE
        )

        if self.request.user.role == "TRAINER":

            students = students.filter(
                batch__trainer=self.request.user
            )

        student_id = self.request.GET.get("student")

        history = []

        selected_student = None

        present = 0

        leave = 0

        absent = 0

        percentage = 0

        if student_id:

            selected_student = get_object_or_404(students, pk=student_id)

            history = Attendance.objects.filter(

                student=selected_student

            ).order_by("-attendance_date")

            present = history.filter(

                status=Attendance.Status.PRESENT

            ).count()

            leave = history.filter(

                status=Attendance.Status.LEAVE

            ).count()

            absent = history.filter(

                status=Attendance.Status.ABSENT

            ).count()

            total = present  + absent

            if total:

                percentage = round(

                    ((present) / total) * 100,

                    2

                )

        context["students"] = students

        context["selected_student"] = selected_student

        context["history"] = history

        context["present"] = present

        context["leave"] = leave

        context["absent"] = absent

        context["percentage"] = percentage

        return context
    
