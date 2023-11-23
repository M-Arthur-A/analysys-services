from fastapi import HTTPException, status


class AppException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class UserAlreadyExistsException(AppException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class IncorrectUnameOrPasswordException(AppException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный логин или пароль"

class TokenExpiredException(AppException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Срок действия токена истек"

class TokenAbsentException(AppException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отсутствует: требуется залогиниться"

class IncorrectTokenFormatException(AppException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена: требуется залогиниться"

class UserIsNotPresentException(AppException):
    status_code=status.HTTP_401_UNAUTHORIZED

class UserIsNotActivatedException(AppException):
    status_code=status.HTTP_409_CONFLICT
