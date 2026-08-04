from dataclasses import dataclass


# slots=True removes __dict__ and prevents dynamic attribute assignment
@dataclass(frozen=True, slots=True)
class ApiInfoItem:
    """Closed value object for an ApiResponse code and message."""

    CODE: str
    MESSAGE: str


class ApiInfo:
    """Namespace for predefined ApiResponse codes and messages."""

    USER_CREATED = ApiInfoItem(
        CODE="USER_CREATED",
        MESSAGE="User created successfully.",
    )

    USER_ALREADY_EXISTS = ApiInfoItem(
        CODE="USER_ALREADY_EXISTS",
        MESSAGE="User already exists.",
    )

    USER_DOES_NOT_EXISTS = ApiInfoItem(
        CODE="USER_DOES_NOT_EXISTS",
        MESSAGE="User does not exists."
    )

    INCORRECT_PASSWORD = ApiInfoItem(
        CODE="INCORRECT_PASSWORD",
        MESSAGE="Password is incorrect.",
    )

    SAME_PASSWORD = ApiInfoItem(
        CODE= "SAME_PASSWORD",
        MESSAGE="New password can not be the same."
    )

    PASSWORD_CHANGED_SUCCESSFULLY = ApiInfoItem(
        CODE="PASSWORD_CHANGED_SUCCESSFULLY",
        MESSAGE="Password changed successfully."
    )

    USER_RETRIEVED = ApiInfoItem(
        CODE="USER_RETRIEVED",
        MESSAGE="User retrieved successfully.",
    )

    INVALID_CREDENTIALS = ApiInfoItem(
        CODE="INVALID_CREDENTIALS",
        MESSAGE="Invalid credentials.",
    )

    TOKEN_CREATED = ApiInfoItem(
        CODE="TOKEN_CREATED",
        MESSAGE="Token created successfully.",
    )

    NOT_AUTHENTICATED = ApiInfoItem(
        CODE="NOT_AUTHENTICATED",
        MESSAGE="Not authenticated.",
    )

    AUTHENTICATION_FAILED = ApiInfoItem(
        CODE="AUTHENTICATION_FAILED",
        MESSAGE="Authentication failed.",
    )

    HTTP_ERROR = ApiInfoItem(
        CODE="HTTP_ERROR",
        MESSAGE="HTTP error.",
    )

    VALIDATION_ERROR = ApiInfoItem(
        CODE="VALIDATION_ERROR",
        MESSAGE="Invalid request data.",
    )

    RESPONSE_VALIDATION_ERROR = ApiInfoItem(
        CODE="RESPONSE_VALIDATION_ERROR",
        MESSAGE="Invalid response data.",
    )

    INTERNAL_SERVER_ERROR = ApiInfoItem(
        CODE="INTERNAL_SERVER_ERROR",
        MESSAGE="Internal server error.",
    )
