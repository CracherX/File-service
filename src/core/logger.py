import logging


def setup_logger(level: str):
    lv = "INFO"
    match level:
        case "INFO":
            lv = logging.INFO
        case "DEBUG":
            lv = logging.DEBUG
    logging.basicConfig(
        level=lv,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("app")
