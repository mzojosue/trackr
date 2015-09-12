import logging
import logging.handlers

from environment import get_log_file

logger = logging.getLogger('trackr_log')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(get_log_file)
logger.addHandler(handler)