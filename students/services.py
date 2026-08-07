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
        face_encoding=result["embedding"],
        is_verified=True
    )

    # Photo has served its purpose (review + encoding). Delete file AND clear field.
    student.photo.delete(save=False)   # removes the file from disk
    student.photo = None               # clears the DB path
    student.save(update_fields=["photo"])

    return True, "Face profile created successfully."