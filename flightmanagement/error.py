class DomainValidationError(ValueError):
    pass

class FieldValidationError(DomainValidationError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)

class MissingMandatoryValueError(ValueError):
    pass

class InvalidDateError(ValueError):
    pass

class InvalidTimeError(ValueError):
    pass

class InvalidIntegerError(ValueError):
    pass

class InvalidFloatError(ValueError):
    pass

class UserCancelled(Exception):
    def __init__(self, message = "\n  Action cancelled."):        
        super().__init__(message)

class RepositoryError(Exception):
    pass

class ForeignKeyInvalidViolation(RepositoryError):
    pass

class UniqueConstraintViolation(RepositoryError):
    pass

class CheckConstraintViolation(RepositoryError):
    pass

class MissingNotNullViolation(RepositoryError):
    pass

class ForeignKeyDependencyViolation(RepositoryError):
    pass

class ConstraintViolation(Exception):
    pass

class FlightNotFound(ValueError):
    pass