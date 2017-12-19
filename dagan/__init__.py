import logging.config

from dagan.resources import resource_path

logging.config.fileConfig(resource_path('log_config.ini'))
