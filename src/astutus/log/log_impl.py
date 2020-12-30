import logging

standard_format = "File \"%(pathname)s:%(lineno)d\" : \n    %(asctime)s [%(levelname)8s] %(message)s"

standard_formatter = logging.Formatter(standard_format)
