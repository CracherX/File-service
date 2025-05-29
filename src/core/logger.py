import logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("uvicorn")

    match level.lower():
        case "DEBUG":
            logger.setLevel(logging.DEBUG)
        case "INFO":
            logger.setLevel(logging.INFO)
        case "WARNING":
            logger.setLevel(logging.WARNING)
        case "ERROR":
            logger.setLevel(logging.ERROR)
        case "CRITICAL":
            logger.setLevel(logging.CRITICAL)

    return logger
