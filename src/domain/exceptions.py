class DomainException(Exception):
    pass

class UnauthorizedException(DomainException):
    pass

class NotFoundException(DomainException):
    pass

class AlreadyExistsException(DomainException):
    pass

class ValidationException(DomainException):
    pass

class ForbiddenException(DomainException):
    pass