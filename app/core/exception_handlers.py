from typing import Any
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

from ..api.response import ApiResponse
from ..api.info import ApiInfo


logger = logging.getLogger(__name__)

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

        ### Logging ###
        log_context = (
            "HTTP exception: %s %s -> %s code=%s",
            request.method,
            request.url.path,
            exc.status_code,
            content.get("code"),
        )
        exception_info = (type(exc), exc, exc.__traceback__)

        if exc.status_code >= 500:
            logger.error(*log_context, exc_info=exception_info)

        # A cause is attached only where the code is explicitly raised 
        # `from e`, so it marks an error worth a full traceback. Ordinary
        # client mistakes carry none and stay one line in log files.
        elif exc.__cause__ is not None:
            logger.warning(*log_context, exc_info=exception_info)
        else:
            logger.info(*log_context)

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

        ### Logging ###
        logger.info(
            "Request Validation Error: %s %s -> %s errors=%s",
            request.method,
            request.url.path,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            validation_errors,
        )

        content = ApiResponse[list[dict[str, Any]]].fail(
            ApiInfo.VALIDATION_ERROR,
            data=validation_errors,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=content,
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(
        request: Request,
        exc: ResponseValidationError,
    ) -> JSONResponse:

        ### Logging ###
        logger.error(
            "Response validation error: %s %s -> %s.",
            request.method,
            request.url.path,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc_info=(type(exc), exc, exc.__traceback__)
        )

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

        ### Logging ###
        logger.error(
            "Unhandled exception: %s %s -> %s.",
            request.method,
            request.url.path,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            exc_info=(type(exc), exc, exc.__traceback__),
        )

        content = ApiResponse[None].error(
            ApiInfo.INTERNAL_SERVER_ERROR,
        ).model_dump(mode="json")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
