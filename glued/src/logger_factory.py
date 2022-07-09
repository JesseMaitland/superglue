import logging
import datetime
from pathlib import Path


def _get_print_stream_format() -> str:
    try:
        from sty import fg
    except ImportError:
        return "%(levelname)s : %(asctime)s : %(message)s"
    else:
        return f"{fg.magenta}%(levelname)s{fg.rs} : {fg.yellow}%(asctime)s{fg.rs} : {fg.cyan}%(message)s{fg.rs}"


def format_logger_filename(name: str = 'glued') -> str:
    name_ts = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%S"))
    return f"{name}-{name_ts}.log"


def logger_factory(
    file_path: Path, logger_name: str, print_stream: bool = True
) -> logging.Logger:
    """
    Args:
        file_path:    The path to the log file to use
        logger_name:  The name to be used by the logger
        print_stream: Set to False to turn off terminal printing

    Returns: logging.Logger

    """

    # parameter for the logger
    logging_level = logging.INFO

    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.setLevel(logging_level)

    # set up the file handler which will be used by all loggers, regardless of their name
    # if we already have the handlers set up, there is no need to set up a new one. This means
    # each time we call the factory, we will get a new logger, with a common file handler.
    if not logger.handlers:

        # set up how we want our messages in the log to look. For the below format they will be
        # LEVEL : TIME : NAME : MESSAGE
        format_string = "%(levelname)s : %(asctime)s : %(name)s : %(message)s"
        date_format = "%m/%d/%Y %I:%M:%S %p"
        formatter = logging.Formatter(fmt=format_string, datefmt=date_format)

        # add the formatter to the file handler, and then attach them to the
        # logging module.
        file_handler = logging.FileHandler(filename=file_path)
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # If we want to print the logs to the terminal as well as logging
        # them to a file, we will add a stream handler to the logger but only
        # in the event that no handlers have been added to the logger already
        if print_stream:
            stream_format = _get_print_stream_format()
            stream_formatter = logging.Formatter(fmt=stream_format, datefmt=date_format)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(stream_formatter)
            logger.addHandler(stream_handler)

    return logger
