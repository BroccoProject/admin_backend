class DomainException(Exception):
    """Base class for all domain exceptions."""
    pass

class ResourceInUseError(DomainException):
    """Raised when a resource cannot be deleted because it is still in use (foreign key constraint)."""
    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.detail = detail
