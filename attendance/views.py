import base64
import os
import uuid
from .utils import is_holiday

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .services import mark_attendance

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView

from .models import Attendance


class AttendanceView(View):

    template_name = "attendance/attendance_home.html"

    def get(self, request):

        return render(
            request,
            self.template_name
        )

    def post(self, request):

        image_data = request.POST.get("image")

        if not image_data:

            return JsonResponse({

                "success": False,

                "message": "No image received."

            })

        if is_holiday():

            return JsonResponse({

                "success": False,

                "message": "Today is a holiday. Attendance cannot be marked."

            })

        try:

            header, encoded = image_data.split(",", 1)

            image_bytes = base64.b64decode(encoded)

            upload_dir = os.path.join(

                settings.MEDIA_ROOT,

                "attendance"

            )

            os.makedirs(

                upload_dir,

                exist_ok=True

            )

            filename = f"{uuid.uuid4().hex}.png"

            image_path = os.path.join(

                upload_dir,

                filename

            )

            with open(image_path, "wb") as image_file:

                image_file.write(image_bytes)

            result = mark_attendance(image_path)
            
            if os.path.exists(image_path):

                os.remove(image_path)

            if result["success"]:


                return JsonResponse({

                    "success": True,

                    "student": str(result["student"]),

                    "confidence": result["attendance"].confidence_score,

                    "message": result["message"]

                })

            if os.path.exists(image_path):

                os.remove(image_path)

            return JsonResponse(result)

        except Exception as e:

            return JsonResponse({

                "success": False,

                "message": str(e)

            })
            
