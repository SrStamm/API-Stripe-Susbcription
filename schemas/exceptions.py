from fastapi import HTTPException, status


class NotAuthorized(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with user_id {user_id} is Not Authorized",
        )


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Not Authorized"
        )


class UserNotFoundInLogin(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class LoginError(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect"
        )


class UserWithEmailExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Ya existe un usuario con este Email",
        )


class UserNotFoundError(HTTPException):
    def __init__(self, id):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )


class DatabaseError(HTTPException):
    def __init__(self, error, func: str):
        self.error = error
        self.func = func
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"database error en {func}: {str(error)}",
        )


class SessionNotFound(HTTPException):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found for user"
        )


class SubscriptionNotFound(HTTPException):
    def __init__(self, sub_id: str):
        self.sub_id = sub_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription {sub_id} not found",
        )


class PlanNotFound(HTTPException):
    def __init__(self, id: str):
        self.id = id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {id} not found",
        )
