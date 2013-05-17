class MultipleImagesWithSameNameError(Exception):
    """Raised if two images pretend to generate the same CSS class name."""
    error_code = 2


class SourceImagesNotFoundError(Exception):
    """Raised if a folder doesn't contain any valid image."""
    error_code = 3


class NoSpritesFoldersFoundError(Exception):
    """Raised if no sprites folders could be found."""
    error_code = 4


class InvalidImageAlgorithmError(Exception):
    """Raised if the provided algorithm name is invalid."""
    error_code = 5


class InvalidImageOrderingError(Exception):
    """Raised if the provided ordering is invalid."""
    error_code = 6


class PILUnavailableError(Exception):
    """Raised if some PIL decoder isn't available."""
    error_code = 7
