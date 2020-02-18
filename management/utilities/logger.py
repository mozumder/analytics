import multiprocessing
import threading
import os
import logging
import time
import pickle
import inspect

from django.db import connection
from django.core.cache import cache
from django.utils import timezone

from analytics.__init__ import *
from analytics.signals import *


try:
    import uwsgi
    import uwsgidecorators
    uwsgi_mode = True
except:
    uwsgi_mode = False

#import sys, codecs

#sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

#logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.DEBUG, format='%(asctime)-15s|%(levelname)-8s|%(process)d|%(name)s|%(module)s|%(message)s')

logger = logging.getLogger("django")
dblogger = logging.getLogger("database")

class logMessage:
    timestamp = None
    ip = None
    response_time = None
    status_code = None
    url = None
    request_content_type = None
    request_method = None
    ajax = False
    preview = False
    prefetch = False
    referer = None
    user_agent = None
    request_content_length = 0
    accept = None
    accept_language = None
    accept_encoding = None
    response_content_type = None
    response_content_length = 0
    compress = None
    session_key = None
    user_id = None
    latitude = None
    longitude = None
    protocol = None
    cached = False
    session_start_time = None


class LogWriter():
    log_sql = 'log'
    def __init__(self, cursor=None, lock=None):
        self.cursor = cursor
        self._lock = lock

    def threaded_write(self, msg=None):
        self.write(self.cursor, self._lock, msg)

    @staticmethod
    def write(cursor, lock, msg=None):
        if uwsgi_mode:
            msg = pickle.loads(msg)
#        msg = self.msg
        with lock:
            cursor.execute("execute " + LogWriter.log_sql + "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", [
                msg.timestamp,
                msg.ip,
                msg.response_time,
                msg.status_code,
                msg.url[:508] + (msg.url[508:] and '..') if msg.url else None,
                msg.request_content_type[:48] + (msg.request_content_type[48:] and '..') if msg.request_content_type else None,
                msg.request_method,
                msg.ajax,
                msg.referer[:508] + (msg.referer[508:] and '..') if msg.referer else None,
                msg.user_agent[:252] + (msg.user_agent[252:] and '..') if msg.user_agent else None,
                msg.request_content_length,
                msg.accept[:252] + (msg.accept[252:] and '..') if msg.accept else None,
                msg.accept_language[:48] + (msg.accept_language[48:] and '..') if msg.accept_language else None,
                msg.accept_encoding[:48] + (msg.accept_encoding[48:] and '..') if msg.accept_encoding else None,
                msg.response_content_type[:48] + (msg.response_content_type[48:] and '..') if msg.response_content_type else None,
                msg.response_content_length,
                msg.compress,
                msg.session_key,
                msg.user_id,
                msg.latitude,
                msg.longitude,
                msg.protocol,
                msg.cached,
                msg.session_start_time,
                msg.preview,
                msg.prefetch,
                msg.bot
            ])
            result = cursor.fetchone()
        log_time = timezone.localtime(result[1]).strftime("%Y-%m-%d %H:%M:%S.%f")
        log_response_time = (result[6]-result[1]).microseconds/1000
#        log_response_time = (time.perf_counter()-msg.perf_counter)*1000
        analytics_logger = logging.getLogger("analytics")
        analytics_logger.info(
            f'{log_time} |'
            f' {msg.ip} |'
            f' {result[5]:.3f}ms |'
            f' {msg.url} |'
            f' {msg.cached} |'
            f' {msg.referer} |'
            f' {msg.user_agent} |'
            f' {msg.session_key} |'
            f' {msg.user_id} |'
            f' {msg.status_code} |'
            f' {msg.response_content_length} bytes |'
            f' {log_response_time:.3f}ms |'
            f' {msg.session_start_time} |'
        )
        
    @staticmethod
    def create_log_message(response):
    
        msg = logMessage()

        msg.timestamp = response.request.timestamp
        msg.perf_counter = response.request.perf_counter
        msg.response_time = (time.perf_counter()-response.request.perf_counter)*1000
        msg.ip = response.get_client_ip(response.request)
        if 'REQUEST_METHOD' in response.request.META:
            method = response.request.META['REQUEST_METHOD']
            if method in METHOD_CHOICES_LOOKUP:
                msg.request_method = METHOD_CHOICES_LOOKUP[method]
            else:
                msg.request_method = UNKNOWN
        else:
            msg.request_method = UNKNOWN
        msg.url = response.request.build_absolute_uri()
        msg.ajax = response.request.is_ajax()
        purpose = response.request.META.get('HTTP_X_PURPOSE')
        moz = response.request.META.get('HTTP_X_MOZ')
        if purpose:
            if purpose.lower() == 'preview':
                msg.preview = True
                msg.prefetch = False
            elif purpose.lower() == 'prefetch':
                msg.preview = False
                msg.prefetch = True
            else:
                msg.preview = False
                msg.prefetch = False
        elif moz:
            if moz.lower() == 'preview':
                msg.preview = True
                msg.prefetch = False
            elif moz.lower() == 'prefetch':
                msg.preview = False
                msg.prefetch = True
            else:
                msg.preview = False
                msg.prefetch = False
        else:
            msg.preview = False
            msg.prefetch = False
        msg.bot = response.request.bot
        msg.accept = response.request.META.get('HTTP_ACCEPT')
        msg.accept_language = response.request.META.get('HTTP_ACCEPT_LANGUAGE')
        msg.accept_encoding = response.request.META.get('HTTP_ACCEPT_ENCODING')
        msg.referer = response.request.META.get('HTTP_REFERER')
        msg.user_agent = response.request.META.get('HTTP_USER_AGENT')
        if 'CONTENT_TYPE' in response.request.META:
            msg.request_content_type = response.request.META['CONTENT_TYPE']
        else:
            msg.request_content_type = None
        if 'CONTENT_LENGTH' in response.request.META.keys():
            if response.request.META['CONTENT_LENGTH']:
                msg.request_content_length = response.request.META['CONTENT_LENGTH']
            else:
                msg.request_content_length = None
        else:
            msg.request_content_length = None
        if 'SERVER_PROTOCOL' in response.request.META:
            server_protocol = response.request.META['SERVER_PROTOCOL']
            if server_protocol in PROTOCOL_CHOICES_LOOKUP:
                msg.protocol = PROTOCOL_CHOICES_LOOKUP[server_protocol]
            else:
                msg.protocol = UNKNOWN
        else:
            msg.protocol = UNKNOWN
        
        msg.status_code = response.status_code

        msg.cached = response.cached
        if 'content-encoding' in response:
            if response['content-encoding'] == 'deflate':
                msg.compress = DEFLATE
            elif response['content-encoding'] == 'gzip':
                msg.compress = GZIP
            else:
                msg.compress = UNCOMPRESSED
        else:
            msg.compress = UNCOMPRESSED
        
        msg.session_key = response.request.session.session_key
        if msg.session_key:
            user = response.request.session.get('_auth_user_id')
            if user:
                msg.user_id = int(user)
            else:
                msg.user_id = None
        else:
            msg.user_id = None
        msg.session_start_time = response.request.session.get('session_start_time')
        if response.__class__.__name__ == 'StreamingHTMLAnalyticResponse':
            # lol race condition where we have to wait for cache populating
            # waiting 50 ms should be enough.
            # Should convert to Python 3.5+ async/await or a signaling framework,
            # but it's in another process.
#            if not msg.cached:
#                time.sleep(.05)
            cache_content = cache.get(response.pageKey)
            if cache_content == None:
                #doh! cache already expired before we could measure it.
                msg.response_content_length = response.length
            else:
                msg.response_content_length = len(cache_content)
        else:
            msg.response_content_length = response.length

        msg.response_content_type = msg.request_content_type
        
        msg.latitude = None
        msg.longitude = None

        return msg

    
    def log(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        self.write(self.cursor, self._lock, msg)

    def log_multiprocess(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        self.q.put(msg)
        self.e.set()

    def log_uwsgi(self, sender, response, **kwargs):
        msg = self.create_log_message(response)
        picklestring = pickle.dumps(msg)
        uwsgi.mule_msg(picklestring,1)

    if not uwsgi_mode:
        q = multiprocessing.Queue()
        e = multiprocessing.Event()
        @staticmethod
        def log_process_listener(e,q):
            cursor=connection.cursor()
            dblogger = logging.getLogger("database")
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
                    try:
                        cursor.execute('deallocate log;')
                    except:
                        pass
                    cursor.execute(sql_commands)

            lock=threading.Lock()
            logwriter = LogWriter(
                cursor=cursor,
                lock=lock
            )
            while True:
                event_is_set = e.wait()
                msg = q.get()
                logwriter.threaded_write(msg)
                e.clear()


