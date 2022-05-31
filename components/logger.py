import logging
from colorama import init

_LOGGER_INITIALIZED = False

# Logging formatter supporting colorized output
class ColoredStreamHandler(logging.StreamHandler):

    CRITICAL_COLOR = "\033[1;35m"  # bright/bold magenta
    ERROR_COLOR = "\033[1;31m"  # bright/bold red
    WARNING_COLOR = "\033[1;33m"  # bright/bold yellow
    INFO_COLOR = "\033[1;32m"  # bright/bold green
    DEBUG_COLOR = "\033[1;34m"  # bright/bold blue

    RESET_CODE = "\033[0m"
    FORMATS = {
        logging.CRITICAL: CRITICAL_COLOR,
        logging.ERROR: ERROR_COLOR,
        logging.WARNING: WARNING_COLOR,
        logging.INFO: INFO_COLOR,
        logging.DEBUG: DEBUG_COLOR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        text = super().format(record)
        color = str(self.FORMATS.get(record.levelno))
        return color + text + self.RESET_CODE


# Setup logging
def init_logger(
    enable_stream: bool = False,
    file_name: str = "",
    enable_file: bool = False,
    log_level: int = logging.INFO,
):
    """
    log_level:
        CRITICAL_MIN -> 50
        ERROR_MIN -> 40
        WARNING_MIN -> 30
        INFO_MIN -> 20 (default)
        DEBUG_MIN -> 10
    """
    global _LOGGER_INITIALIZED
    if not _LOGGER_INITIALIZED:
        _LOGGER_INITIALIZED = True
        init()
    else:
        return

    if log_level < 0 or log_level > 50:
        log_level = logging.DEBUG
    else:
        log_level = log_level - log_level % 10
    handlers = []
    colored_stream = ColoredStreamHandler() if enable_stream else logging.NullHandler()

    msg_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    colored_stream.setFormatter(logging.Formatter(msg_format))
    handlers.append(colored_stream)
    if enable_file and file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(logging.Formatter(msg_format))
        handlers.append(file_handler)

    logging.basicConfig(level=log_level, handlers=handlers)


if __name__ == "__main__":
    init_logger(enable_stream=True)
    messaggio = "hello"
    log = logging.getLogger("World")
    log.debug(messaggio)
    log.info(messaggio)
    log.warning(messaggio)
    try:
        y = 1 / 0
    except Exception as e:
        error_message = e.__repr__()
        log.exception(error_message)
    log.error(messaggio)
    log.critical(messaggio)
