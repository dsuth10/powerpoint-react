from loguru import logger
import sys
import contextvars

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


def setup_logging():
    logger.remove()
    logger.add(sys.stdout, serialize=True, level="INFO")

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