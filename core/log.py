import logging
import logging.handlers

logger = logging.getLogger('trackr_log')
logger.setLevel(logging.DEBUG)
try:
	handler = logging.handlers.RotatingFileHandler('campa.log')
except IOError:
	# avoid absolute path to catch sandbox IOError during testing
	handler = logging.handlers.RotatingFileHandler('campa.log')
logger.addHandler(handler)
