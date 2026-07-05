from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel


API_RESPONSE_MODEL = TypeVar("API_RESPONSE_MODEL")


@dataclass(frozen=True, slots=True)
class ApiInfoItem:
    CODE: str
    MESSAGE: str


class ApiInfo:
    USER_CREATED = ApiInfoItem(
        CODE="USER_CREATED",
        MESSAGE="User created successfully.",
    )

    USER_ALREADY_EXISTS = ApiInfoItem(
        CODE="USER_ALREADY_EXISTS",
        MESSAGE="User already exists.",
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


class ApiResponse(BaseModel, Generic[API_RESPONSE_MODEL]):
    status: Literal["success", "fail", "error"]
    code: str
    message: str
    data: API_RESPONSE_MODEL | None = None

    @classmethod
    def success(
        cls,
        info: ApiInfoItem,
        data: API_RESPONSE_MODEL | None = None,
    ) -> ApiResponse[API_RESPONSE_MODEL]:

        return cls(
            status="success",
            code=info.CODE,
            message=info.MESSAGE,
            data=data,
        )

    @classmethod
    def fail(
        cls,
        info: ApiInfoItem,
        data: API_RESPONSE_MODEL | None = None,
    ) -> ApiResponse[API_RESPONSE_MODEL]:

        return cls(
            status="fail",
            code=info.CODE,
            message=info.MESSAGE,
            data=data,
        )

    @classmethod
    def error(
        cls,
        info: ApiInfoItem,
        data: API_RESPONSE_MODEL | None = None,
    ) -> ApiResponse[API_RESPONSE_MODEL]:

        return cls(
            status="error",
            code=info.CODE,
            message=info.MESSAGE,
            data=data,
        )
