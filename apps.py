from django.apps import AppConfig
from django.db import connection
from django.conf import settings
import multiprocessing

from django.db.backends.signals import connection_created

from unchained.apps import PreparedAppConfig

from analytics.management.utilities.logger import LogWriter
from analytics.signals import *

try:
    import uwsgi
    import uwsgidecorators
    uwsgi_mode = True
except:
    uwsgi_mode = False

class AnalyticsConfig(PreparedAppConfig):
    name = 'analytics'
    verbose_name = "Logging & Analytics"
    sql_dirs = (
        'analytics/sql',
    )

    def ready(self):

        connection_created.connect(self.prepareSQL, dispatch_uid="prepareAnalyticsDb")
        
        self.logwriter = LogWriter()
        try:
            MULTIPROCESS = settings.MULTIPROCESS
        except:
            MULTIPROCESS = False
        if MULTIPROCESS:
            if uwsgi_mode:
                log_response.connect(self.logwriter.log_uwsgi, dispatch_uid="log_response")
            else:
                log_process = multiprocessing.Process(name='Logging', target=LogWriter.log_process_listener, args=(LogWriter.e,LogWriter.q,))
                log_process.daemon=True
                log_process.start()
                log_response.connect(self.logwriter.log_multiprocess, dispatch_uid="log_response")
        else:
            log_response.connect(self.logwriter.log, dispatch_uid="log_response")

