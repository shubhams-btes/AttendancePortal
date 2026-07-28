from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from accounts.models import CustomUser
from attendance.models import Attendance
from batches.models import Batch
from students.models import Student



class DashboardView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.request.user
        context["is_admin"] = user.role == CustomUser.Role.ADMIN
        
        if user.role == CustomUser.Role.ADMIN:

            context["total_students"] = Student.objects.count()

            context["active_batches"] = Batch.objects.filter(
                status=Batch.Status.ACTIVE
            ).count()

            context["total_trainers"] = CustomUser.objects.filter(
                role=CustomUser.Role.TRAINER,
                is_active=True
            ).count()

            context["today_attendance"] = Attendance.objects.filter(
                attendance_date=date.today()
            ).count()

            context["recent_batches"] = Batch.objects.select_related(
                "trainer"
            ).order_by("-created_at")[:5]

            context["recent_students"] = Student.objects.select_related(
                "batch"
            ).order_by("-registration_date")[:5]
            
            

        else:

            trainer_batches = Batch.objects.filter(
                trainer=user
            )
            
           

            active_students = Student.objects.filter(
                batch__in=trainer_batches,
                status=Student.Status.ACTIVE
            )

            student_count = active_students.count()

            present_count = Attendance.objects.filter(
                student__in=active_students
            ).count()

            days_running = 0

            for batch in trainer_batches:
                if batch.start_date <= date.today():
                    days_running = max(
                        days_running,
                        (date.today() - batch.start_date).days + 1
                    )

            expected_attendance = student_count * days_running

            if expected_attendance:
                overall_attendance = round(
                    (present_count / expected_attendance) * 100,
                    2
                )
            else:
                overall_attendance = 0

            context["overall_attendance"] = overall_attendance

            context["total_students"] = Student.objects.filter(
                batch__in=trainer_batches
            ).count()

            context["active_batches"] = trainer_batches.filter(
                status=Batch.Status.ACTIVE
            ).count()

            context["total_trainers"] = 1

            context["today_attendance"] = Attendance.objects.filter(
                student__batch__in=trainer_batches,
                attendance_date=date.today()
            ).count()

            context["recent_batches"] = trainer_batches.order_by(
                "-created_at"
            )[:5]

            context["recent_students"] = Student.objects.filter(
                batch__in=trainer_batches
            ).select_related("batch").order_by(
                "-registration_date"
            )[:5]

        return context