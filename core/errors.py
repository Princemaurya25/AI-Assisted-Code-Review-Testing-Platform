from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class APIException(HTTPException):
    def __init__(self, status_code: int, message: str, details: dict = None):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.details = details or {}


async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, APIException):
        logger.warning(f"API Exception on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details}
        )
    
    logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An internal server error occurred. Please try again later."}
    )
