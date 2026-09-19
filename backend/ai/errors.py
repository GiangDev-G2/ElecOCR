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


class ModelLoadError(ElecOcrError):
    """Raised when model weights or dependencies fail to load."""


class DisplayRegionNotFoundError(ElecOcrError):
    """Raised when detector fails to find the meter display region."""


class UnreadableMeterError(ElecOcrError):
    """Raised when the meter reading cannot be determined with confidence."""


class InferenceError(ElecOcrError):
    """Raised when a runtime error occurs during neural inference."""


class ConfigurationError(ElecOcrError):
    """Raised when system or training configuration is invalid."""
