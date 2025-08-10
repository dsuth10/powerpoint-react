from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from loguru import logger

def add_error_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.bind(path=request.url.path, status=exc.status_code).error(
            "HTTPException: {detail}", detail=exc.detail
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.bind(path=request.url.path).exception("Unhandled Exception")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"}) 