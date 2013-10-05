class GlueError(Exception):
    """Base Exception class for glue Errors."""
    error_code = 999


class PILUnavailableError(GlueError):
    """Raised if some PIL decoder isn't available."""
    error_code = 2


class ValidationError(GlueError):
    """Raised by formats or sprites while ."""
    error_code = 3


class SourceImagesNotFoundError(GlueError):
    """Raised if a folder doesn't contain any valid image."""
    error_code = 4


class NoSpritesFoldersFoundError(GlueError):
    """Raised if no sprites folders could be found."""
    error_code = 5
