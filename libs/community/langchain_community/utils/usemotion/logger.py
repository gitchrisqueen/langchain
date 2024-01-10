import logging
from logging.handlers import RotatingFileHandler

# Setup logger
logger = logging.getLogger(__name__)
FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
# Log to file
logging_filename = 'motion.debug.log'
handler = RotatingFileHandler(logging_filename, maxBytes=250000000, backupCount=10)  # 10 files of 250MB each
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)
