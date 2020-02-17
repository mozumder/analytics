import logging
import threading

from django.db import connection

from analytics.management.utilities.logger import LogWriter
from uwsgi import mule_get_msg

logger = logging.getLogger("django")
dblogger = logging.getLogger("database")

lock=threading.Lock()
cursor=connection.cursor()

file_name = 'analytics/include/sql/prepare.sql'
try:
    file = open(file_name, 'r')
except FileNotFoundError:
    dblogger.debug('No SQL file: %s' % file_name)
    pass
except (OSError, IOError) as e:
    dblogger.error('Error reading SQL file: %s' % file_name)
    raise e
else:
    sql_commands=file.read().strip()
    if sql_commands:
        cursor.execute(sql_commands)

def listener():
    global cursor
    global lock
    logwriter = LogWriter(
        cursor=cursor,
        lock=lock
    )
    logger.info("uWSGI Log Mule Process started & listening")
    while True:
        msg = mule_get_msg()
        logwriter.threaded_write(msg)

if __name__ == '__main__':
    listener()
