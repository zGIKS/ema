class DomainError(Exception):
    """Base error for domain/application layer failures."""


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass
