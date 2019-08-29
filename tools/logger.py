
import logging
import logging.config
from logging_conf import SRC_LOGGING_CONF

logging.config.dictConfig(SRC_LOGGING_CONF)
logger = logging.getLogger("src")