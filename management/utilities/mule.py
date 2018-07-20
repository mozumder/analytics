import logging
logger = logging.getLogger("django")

from analytics.management.utilities.logger import LogWriter
from uwsgi import mule_get_msg

logger.info("uWSGI Log Mule Process started & listening")
while True:
    msg = mule_get_msg()
    LogWriter.write(msg)

