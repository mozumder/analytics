from django.apps import AppConfig
from django.db import connection
from django.conf import settings
import multiprocessing

from django.db.backends.signals import connection_created

from unchained.apps import PreparedAppConfig

from analytics.management.utilities.logger import LogWriter
from analytics.signals import log_response

try:
    import uwsgi
    import uwsgidecorators
    uwsgi_mode = True
except:
    uwsgi_mode = False

import logging
logger = logging.getLogger("django")

class AnalyticsConfig(PreparedAppConfig):
    name = 'analytics'
    verbose_name = "Logging & Analytics"
    dbConnectSignal = 'prepareAnalyticsDb'

    sql_dirs = (
            'analytics/include/sql',
            )

    def db_connected(self,sender, connection, **kwargs):
        super().db_connected(sender, connection, **kwargs)
        self.logwriter.connection = connection
        self.logwriter.cursor = connection.cursor()

    def ready(self):
        connection_created.connect(self.db_connected, dispatch_uid=self.dbConnectSignal)

        self.logwriter = LogWriter(None)

        try:
            MULTIPROCESS = settings.MULTIPROCESS
        except:
            MULTIPROCESS = False
        if MULTIPROCESS:
            logger.info('Multi process mode!')
            if uwsgi_mode:
                logger.info('UWSGI mode!')
                log_response.connect(self.logwriter.log_uwsgi, dispatch_uid="log_response")
            else:
                logger.info('Runserver mode =^(')
                log_process = multiprocessing.Process(name='Logging', target=LogWriter.log_process_listener, args=(LogWriter.e,LogWriter.q))
                log_process.daemon=True
                log_process.start()
                log_response.connect(self.logwriter.log_multiprocess, dispatch_uid="log_response")
        else:
            logger.info('Single Processor mode =^(')
            log_response.connect(self.logwriter.log, dispatch_uid="log_response")
