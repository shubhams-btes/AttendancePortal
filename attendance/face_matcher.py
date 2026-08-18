import cv2
import numpy as np

from insightface.app import FaceAnalysis

from students.models import FaceProfile


app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


def recognize_face(image_path, threshold=0.65):
    """
    Compare the captured image with all registered students.

    Returns:
        success
        student
        confidence
        message
    """

    image = cv2.imread(str(image_path))

    if image is None:

        return {
            "success": False,
            "retry": True,
            "message": "Unable to read image."
        }

    faces = app.get(image)

    if len(faces) == 0:

        return {
            "success": False,
            "retry": True,
            "message": "No face detected."
        }

    if len(faces) > 1:

        return {
            "success": False,
            "retry": True,
            "message": "Multiple faces detected."
        }

    embedding = faces[0].embedding

    best_student = None

    best_similarity = -1

    profiles = FaceProfile.objects.filter(
        is_verified=True
    ).select_related("student")

    for profile in profiles:

        stored = np.array(
            profile.face_encoding,
            dtype=np.float32
        )

        similarity = np.dot(
            embedding,
            stored
        ) / (
            np.linalg.norm(embedding)
            *
            np.linalg.norm(stored)
        )

        if similarity > best_similarity:

            best_similarity = similarity

            best_student = profile.student

    if best_student is None or best_similarity < threshold:
        return {"success": False, "retry": False, "message": "Face not recognized."}

    return {
        "success": True,
        "student": best_student,
        "confidence": round(float(best_similarity * 100), 2),
    }