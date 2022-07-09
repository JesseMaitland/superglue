from glued.src.logger_factory import format_logger_filename, logger_factory
from glued.environment.variables import GLUED_LOGGER_DIR


def get_logger(name: str):
    logger_file = format_logger_filename()
    logger = logger_factory(file_path=GLUED_LOGGER_DIR.joinpath(logger_file), logger_name=name)
    return logger
