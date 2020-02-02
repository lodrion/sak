"""Helper utilities for logging"""
import logging
import sys
from typing import List


LOGGING_FORMAT = "%(asctime)s %(levelname)s\t%(name)s:%(lineno)s\t%(message)s"


def setup(log_level_str: str = 'INFO') -> None:
    """Setup logging for the executable. Should not be called from library code"""
    log_level_int = _get_int_level_or_die(log_level_str)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_int)

    formatter = logging.Formatter(LOGGING_FORMAT)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def quiet_loggers(libraries: List[str], min_log_level_str = 'ERROR'):
    """Make individual libraries' loggers less verbose"""
    log_level_int = _get_int_level_or_die(min_log_level_str)

    for library in libraries:
        logging.getLogger(library).setLevel(log_level_int)


def _get_int_level_or_die(log_level_str: str) -> int:
    """Convert string to int logging level or die trying"""
    log_level_int = logging.getLevelName(log_level_str)
    if not isinstance(log_level_int, int):
        raise ValueError('{} is not a valid logging level name'.format(log_level_str))
    return log_level_int
