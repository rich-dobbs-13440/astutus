import logging
import pkgutil
from typing import Dict, List, Optional, Set, Tuple  # noqa

logger = logging.getLogger(__name__)

console_format = "File \"%(pathname)s:%(lineno)d\" : \n    %(asctime)s [%(levelname)8s] %(message)s"

standard_formatter = logging.Formatter(console_format)


def get_loggers() -> List[logging.Logger]:
    loggers = []
    # Attempt to avoid a circular dependency
    import astutus
    pkg = astutus
    for _, module_name, is_pkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + '.'):
        logger.debug(f"module_name: {module_name}")
        logger.debug(f"is_pkg: {is_pkg}")
        if not is_pkg:
            logger_for_module = logging.getLogger(module_name)
            loggers.append(logger_for_module)
    return loggers


def set_level(logger_name: str, level: int) -> None:
    for logger_for_module in get_loggers():
        if logger_for_module.name == logger_name:
            logger.debug(f"logger_for_module: {logger_for_module.name} was found. ")
            logger_for_module.setLevel(int(level))
            return
    assert False, (logger_name, level)
