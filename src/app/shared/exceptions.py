class DomainError(Exception):
    """Base error for domain/application layer failures."""


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ExternalServiceError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass
