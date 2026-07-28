import cv2
import numpy as np

from insightface.app import FaceAnalysis


# Load the model only once when Django starts
app = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


def extract_face_data(image_path):
    """
    Detect exactly one face and return:
    - success
    - message
    - embedding
    """

    image = cv2.imread(str(image_path))

    if image is None:
        return {
            "success": False,
            "message": "Unable to read image."
        }

    faces = app.get(image)

    if len(faces) == 0:
        return {
            "success": False,
            "message": "No face detected."
        }

    if len(faces) > 1:
        return {
            "success": False,
            "message": "Multiple faces detected."
        }

    face = faces[0]

    embedding = face.embedding.tolist()

    return {
        "success": True,
        "message": "Face verified.",
        "embedding": embedding
    }