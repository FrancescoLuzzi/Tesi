import logging
from colorama import init

is_initialized = False

# Logging formatter supporting colorized output
class ColoredStreamHandler(logging.StreamHandler):

    CRITICAL_COLOR = "\033[1;35m"  # bright/bold magenta
    ERROR_COLOR = "\033[1;31m"  # bright/bold red
    WARNING_COLOR = "\033[1;33m"  # bright/bold yellow
    INFO_COLOR = "\033[1;32m"  # bright/bold green
    DEBUG_COLOR = "\033[1;34m"  # bright/bold blue

    RESET_CODE = "\033[0m"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FORMATS = {
            logging.CRITICAL: self.CRITICAL_COLOR,
            logging.ERROR: self.ERROR_COLOR,
            logging.WARNING: self.WARNING_COLOR,
            logging.INFO: self.INFO_COLOR,
            logging.DEBUG: self.DEBUG_COLOR,
        }

    def my_format(self, package):
        return (
            f"{package['from']}: {package['message']}" if "from" in package else package
        )

    def format(self, record):
        record.msg = self.my_format(record.msg)
        text = super().format(record)
        color = str(self.FORMATS.get(record.levelno))
        return color + text + self.RESET_CODE


# Setup logging
def init_logger(file_name: str = "", log_level: int = 10, enable_file: bool = False):
    """
    set log_level:
        CRITICAL_MIN -> 50
        ERROR_MIN -> 40
        WARNING_MIN -> 30
        INFO_MIN -> 20
        DEBUG_MIN -> 10

    message_format = { "from": "from_who", "message": "payload" } || "message"
    """
    global is_initialized
    if not is_initialized:
        is_initialized = True
        init()
    else:
        return

    if log_level < 0 or log_level > 50:
        log_level = logging.DEBUG
    else:
        log_level = log_level - log_level % 10
    handlers = []
    colored_stream = ColoredStreamHandler()

    msg_format = "%(asctime)s [%(levelname)s] %(message)s"

    colored_stream.setFormatter(logging.Formatter(msg_format))
    handlers.append(colored_stream)
    if enable_file and file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(logging.Formatter(msg_format))
        handlers.append(file_handler)

    logging.basicConfig(level=log_level, handlers=handlers)


if __name__ == "__main__":
    init_logger()
    messaggio = {"from": "prova", "message": "messaggio di prova"}
    logging.debug(messaggio)
    logging.info(messaggio)
    logging.warning(messaggio)
    try:
        y = 1 / 0
    except Exception as e:
        error_message = messaggio
        error_message["message"] = e.__repr__()
        logging.exception(error_message)
    logging.error(messaggio)
    logging.critical(messaggio)
