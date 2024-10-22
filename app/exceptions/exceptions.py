from fastapi import HTTPException


class CloudStackApiException(HTTPException):
    """base exception class"""

    def __init__(self, status_code: int, detail: str, headers: dict | None = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.status_code, self.detail)


class ServiceException(CloudStackApiException):
    """failures in external services or APIs, like a database or a third-party service"""

    pass


class EntityDoesNotExistException(CloudStackApiException):
    """database returns nothing"""

    pass


class EntityAlreadyExistsException(CloudStackApiException):
    """conflict detected, like trying to create a resource that already exists"""

    pass


class InvalidOperationException(CloudStackApiException):
    """invalid operations like trying to delete a non-existing entity, etc."""

    pass


class InvalidCredentialsException(CloudStackApiException):
    """invalid authentication credentials"""

    pass


class InvalidTokenException(CloudStackApiException):
    """invalid token"""

    pass
