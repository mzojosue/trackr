import logging
import logging.handlers

from environment import get_log_file

logger = logging.getLogger('trackr_log')
logger.setLevel(logging.DEBUG)
try:
	handler = logging.handlers.RotatingFileHandler(get_log_file)
except IOError:
	# avoid absolute path to catch sandbox IOError during testing
	handler = logging.handlers.RotatingFileHandler('campa.log')
logger.addHandler(handler)
