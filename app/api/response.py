from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from .info import ApiInfoItem


class ApiResponse[RESPONSE_MODEL](BaseModel):
    """
    Standard API response format with status, code, message, and optional data.
    """

    status: Literal["success", "fail", "error"]
    code: str
    message: str
    data: RESPONSE_MODEL | None = None

    @classmethod
    def success(
        cls,
        info: ApiInfoItem,
        # pydantic converts an ORM object into RESPONSE_MODEL through from_attributes
        # and type checker cannot confirm that conversion actually happened, therefore
        # add 'Any' to avoid type errors
        data: RESPONSE_MODEL | Any = None,
    ) -> ApiResponse[RESPONSE_MODEL]:

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
        data: RESPONSE_MODEL | Any = None,
    ) -> ApiResponse[RESPONSE_MODEL]:

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
        data: RESPONSE_MODEL | Any = None,
    ) -> ApiResponse[RESPONSE_MODEL]:

        return cls(
            status="error",
            code=info.CODE,
            message=info.MESSAGE,
            data=data,
        )
