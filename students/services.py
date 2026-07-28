from .face_utils import extract_face_data
from .models import FaceProfile


def create_face_profile(student):
    """
    Generate face embedding for a registered student.

    Returns:
        (success, message)
    """

    result = extract_face_data(student.photo.path)

    if not result["success"]:
        return False, result["message"]

    FaceProfile.objects.create(
        student=student,
        face_image=student.photo,
        face_encoding=result["embedding"],
        is_verified=True
    )

    return True, "Face profile created successfully."