from loguru import logger
import sys
import json

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