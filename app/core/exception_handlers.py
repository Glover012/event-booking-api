from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

from ..api.response import ApiResponse
from ..api.info import ApiInfo


def register_custom_exception_handlers(app: FastAPI) -> None:
    """
    Function that set custom exception handlers.
    Uses custom ApiResponse body format.
    """
    ### Exception Handlers ###
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:

        if isinstance(exc.detail, ApiResponse):
            content = exc.detail.model_dump(mode="json")
        else:
            response_status = "error" if exc.status_code >= 500 else "fail"

            content = ApiResponse[None](
                status=response_status,
                code=ApiInfo.HTTP_ERROR.CODE,
                message=str(exc.detail),
                data=None,
            ).model_dump(mode="json")

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:

        validation_errors: list[dict[str, Any]] = [
            {
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type"),
            }
            for error in exc.errors()
        ]

        content = ApiResponse[list[dict[str, Any]]].fail(
            ApiInfo.VALIDATION_ERROR,
            data=validation_errors,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=content,
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(
        request: Request,
        exc: ResponseValidationError,
    ) -> JSONResponse:

        content = ApiResponse[None].error(
            ApiInfo.RESPONSE_VALIDATION_ERROR,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:

        content = ApiResponse[None].error(
            ApiInfo.INTERNAL_SERVER_ERROR,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
