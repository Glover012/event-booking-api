from fastapi import HTTPException
from starlette import status

from .info import ApiInfo, ApiInfoItem
from .response import ApiResponse


class HTTPErrorItem(HTTPException):
    """
    HTTPException object for fast raising HTTP Exception across API. 
    Status code, detail and optional headers.
    """

    def __init__(
            self,
            status_code: int,
            info: ApiInfoItem,
            headers: dict[str, str] | None = None
            ) -> None:
        detail = ApiResponse.fail(info)
        super().__init__(status_code, detail, headers)


class HTTPError:
    """
    Collection of predefined ready to use standard HTTP Errors.
    """

    AUTHENTICATION_FAILED = HTTPErrorItem(
        status_code=status.HTTP_401_UNAUTHORIZED,
        info=ApiInfo.AUTHENTICATION_FAILED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    NOT_AUTHENTICATED = HTTPErrorItem(
        status_code=status.HTTP_401_UNAUTHORIZED,
        info=ApiInfo.NOT_AUTHENTICATED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    INVALID_CREDENTIALS = HTTPErrorItem(
        status_code=status.HTTP_401_UNAUTHORIZED,
        info=ApiInfo.INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

    USER_DOES_NOT_EXISTS = HTTPErrorItem(
        status_code=status.HTTP_404_NOT_FOUND,
        info=ApiInfo.USER_DOES_NOT_EXISTS,
    )

    USER_ALREADY_EXISTS = HTTPErrorItem(
        status_code=status.HTTP_409_CONFLICT,
        info=ApiInfo.USER_ALREADY_EXISTS,
    )

    INCORRECT_PASSWORD = HTTPErrorItem(
        status_code=status.HTTP_400_BAD_REQUEST,
        info=ApiInfo.INCORRECT_PASSWORD,
    )

    SAME_PASSWORD = HTTPErrorItem(
        status_code=status.HTTP_400_BAD_REQUEST,
        info=ApiInfo.SAME_PASSWORD,
    )

    FORBIDDEN = HTTPErrorItem(
        status_code=status.HTTP_403_FORBIDDEN,
        info=ApiInfo.FORBIDDEN,
    )

    TRANSACTION_REFUSED = HTTPErrorItem(
        status_code=status.HTTP_409_CONFLICT,
        info=ApiInfo.TRANSACTION_REFUSED,
    )

    EVENT_DOES_NOT_EXIST = HTTPErrorItem(
        status_code=status.HTTP_404_NOT_FOUND,
        info=ApiInfo.EVENT_DOES_NOT_EXIST,
    )
