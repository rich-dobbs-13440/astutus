import logging
import pkgutil
# import os

logger = logging.getLogger(__name__)

console_format = "File \"%(pathname)s:%(lineno)d\" : \n    %(asctime)s [%(levelname)8s] %(message)s"

standard_formatter = logging.Formatter(console_format)


def get_loggers():
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
