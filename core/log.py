from environment import get_log_file

import logging
import logging.handlers

logger = logging.getLogger('trackr_log')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
	get_log_file, maxBytes=50000, backupCount=5)
logger.addHandler(handler)