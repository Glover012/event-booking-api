from dataclasses import dataclass

from fastapi import HTTPException
from starlette import status

from .info import ApiInfo, ApiInfoItem
from .response import ApiResponse


# slots=True removes __dict__ and prevents dynamic attribute assignment
@dataclass(frozen=True, slots=True)
class HTTPErrorItem:
    """
    HTTPException factory for fast raising HTTP Exception across API. 
    Status code, detail and optional headers.

    Returns HTTPException object.
    """

    STATUS_CODE: int
    INFO: ApiInfoItem
    HEADERS: dict[str, str] | None = None

    def __call__(self) -> HTTPException:
        return HTTPException(
            status_code=self.STATUS_CODE,
            detail=ApiResponse.fail(self.INFO),
            headers=self.HEADERS,
        )


class HTTPError:
    """
    Collection of predefined ready to use standard HTTP Errors.

    Raise them by calling:

        raise HTTPError.FORBIDDEN(). 

    In `try except` block, raise them with the original error attached:

        except IntegrityError as e:
            raise HTTPError.TRANSACTION_REFUSED() from e
    """

    AUTHENTICATION_FAILED = HTTPErrorItem(
        STATUS_CODE=status.HTTP_401_UNAUTHORIZED,
        INFO=ApiInfo.AUTHENTICATION_FAILED,
        HEADERS={"WWW-Authenticate": "Bearer"},
    )

    NOT_AUTHENTICATED = HTTPErrorItem(
        STATUS_CODE=status.HTTP_401_UNAUTHORIZED,
        INFO=ApiInfo.NOT_AUTHENTICATED,
        HEADERS={"WWW-Authenticate": "Bearer"},
    )

    INVALID_CREDENTIALS = HTTPErrorItem(
        STATUS_CODE=status.HTTP_401_UNAUTHORIZED,
        INFO=ApiInfo.INVALID_CREDENTIALS,
        HEADERS={"WWW-Authenticate": "Bearer"},
    )

    USER_DOES_NOT_EXISTS = HTTPErrorItem(
        STATUS_CODE=status.HTTP_404_NOT_FOUND,
        INFO=ApiInfo.USER_DOES_NOT_EXISTS,
    )

    USER_ALREADY_EXISTS = HTTPErrorItem(
        STATUS_CODE=status.HTTP_409_CONFLICT,
        INFO=ApiInfo.USER_ALREADY_EXISTS,
    )

    INCORRECT_PASSWORD = HTTPErrorItem(
        STATUS_CODE=status.HTTP_400_BAD_REQUEST,
        INFO=ApiInfo.INCORRECT_PASSWORD,
    )

    SAME_PASSWORD = HTTPErrorItem(
        STATUS_CODE=status.HTTP_400_BAD_REQUEST,
        INFO=ApiInfo.SAME_PASSWORD,
    )

    FORBIDDEN = HTTPErrorItem(
        STATUS_CODE=status.HTTP_403_FORBIDDEN,
        INFO=ApiInfo.FORBIDDEN,
    )

    TRANSACTION_REFUSED = HTTPErrorItem(
        STATUS_CODE=status.HTTP_409_CONFLICT,
        INFO=ApiInfo.TRANSACTION_REFUSED,
    )

    EVENT_DOES_NOT_EXIST = HTTPErrorItem(
        STATUS_CODE=status.HTTP_404_NOT_FOUND,
        INFO=ApiInfo.EVENT_DOES_NOT_EXIST,
    )

    CANNOT_MODIFY_OWN_PERMISSIONS = HTTPErrorItem(
        STATUS_CODE=status.HTTP_403_FORBIDDEN,
        INFO=ApiInfo.CANNOT_MODIFY_OWN_PERMISSIONS,
    )

    SAME_ROLE = HTTPErrorItem(
        STATUS_CODE=status.HTTP_409_CONFLICT,
        INFO=ApiInfo.SAME_ROLE,
    )
