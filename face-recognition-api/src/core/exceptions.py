class FaceRecognitionError(Exception):
    """Error base del dominio."""
    pass


class FaceNotDetectedError(FaceRecognitionError):
    pass


class PersonNotFoundError(FaceRecognitionError):
    pass


class DuplicatePersonError(FaceRecognitionError):
    pass
