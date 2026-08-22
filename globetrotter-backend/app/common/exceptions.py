from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(
        self, detail: str = "Not enough permissions to perform this operation"
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class PayloadTooLargeException(HTTPException):
    def __init__(self, detail: str = "File size exceeds maximum allowed limit"):
        super().__init__(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=detail)


# Aliases for domain layer naming conventions
NotFoundError = NotFoundException
BadRequestError = BadRequestException
UnauthorizedError = UnauthorizedException
ForbiddenError = ForbiddenException
ConflictError = ConflictException
PayloadTooLargeError = PayloadTooLargeException
