"""Domain and application exceptions."""


class ElecOcrError(Exception):
    """Base exception for expected ElecOCR failures."""


class UnsupportedImageError(ElecOcrError):
    """Raised when an upload uses an unsupported media type."""


class InvalidImageError(ElecOcrError):
    """Raised when uploaded bytes cannot be decoded safely as an image."""


class InvalidReadingError(ElecOcrError):
    """Raised when recognizer output violates the reading contract."""


class ImageTooLargeError(ElecOcrError):
    """Raised when byte or pixel limits are exceeded."""


class ModelNotReadyError(ElecOcrError):
    """Raised when inference is requested before models are ready."""
