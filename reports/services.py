from attendance.models import Attendance
from datetime import date
import calendar

class AttendanceService:

    @staticmethod
    def summary(queryset):

        total = queryset.count()

        present = queryset.filter(
            status=Attendance.Status.PRESENT
        ).count()

        late = queryset.filter(
            status=Attendance.Status.LATE
        ).count()

        absent = queryset.filter(
            status=Attendance.Status.ABSENT
        ).count()

        percentage = 0

        if total:

            percentage = round(

                ((present + late) / total) * 100,

                2

            )

        return {

            "total": total,

            "present": present,

            "late": late,

            "absent": absent,

            "percentage": percentage,

        }
        
    @staticmethod
    def trainer_queryset(user, queryset):

        if user.role == "TRAINER":

            return queryset.filter(
                batch__trainer=user
            )

        return queryset
    
    @staticmethod
    def attendance_badge(status):

        badges = {

            Attendance.Status.PRESENT: "success",

            Attendance.Status.LATE: "warning",

            Attendance.Status.ABSENT: "danger",

        }

        return badges.get(status, "secondary")
    
    @staticmethod
    def attendance_percentage(
        present,
        late,
        absent
    ):

        total = present + late + absent

        if total == 0:

            return 0

        return round(

            ((present + late) / total) * 100,

            2

        )
        
class DateService:

    @staticmethod
    def today():

        return date.today()

    @staticmethod
    def current_year():

        return date.today().year

    @staticmethod
    def current_month():

        return date.today().month
    
    @staticmethod
    def month_name(month):

        return calendar.month_name[month]
    
    @staticmethod
    def months():

        return [

            {

                "value": i,

                "name": calendar.month_name[i]

            }

            for i in range(1,13)

        ]