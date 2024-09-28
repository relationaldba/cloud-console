class CloudStackApiError(Exception):
    """base exception class"""

    def __init__(self, message: str = "Service is unavailable", name: str = "CloudStackApiError"):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class ServiceError(CloudStackApiError):
    """failures in external services or APIs, like a database or a third-party service"""

    pass


class EntityDoesNotExistError(CloudStackApiError):
    """database returns nothing"""

    pass


class EntityAlreadyExistsError(CloudStackApiError):
    """conflict detected, like trying to create a resource that already exists"""

    pass


class InvalidOperationError(CloudStackApiError):
    """invalid operations like trying to delete a non-existing entity, etc."""

    pass


class AuthenticationError(CloudStackApiError):
    """invalid authentication credentials"""

    pass


class InvalidTokenError(CloudStackApiError):
    """invalid token"""

    pass