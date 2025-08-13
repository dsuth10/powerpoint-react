from loguru import logger
import sys
import contextvars
import os

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


def setup_logging():
    # Remove default handler
    logger.remove()
    
    # Determine log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Add console handler with detailed formatting
    logger.add(
        sys.stdout, 
        serialize=False,  # Don't serialize for console output
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler for persistent logs
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        compression="zip"
    )

    # Optionally patch uvicorn loggers
    import logging

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers = [InterceptHandler()]


def set_request_id(request_id: str | None) -> None:
    request_id_var.set(request_id)