from django.db import models

from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html

from django.contrib.sessions.models import Session
#import psycopg2

from . import *

import time

from .apps import *

global streaming_length
streaming_length = 0

class IP(models.Model):
    address = models.GenericIPAddressField(verbose_name='IP Address',db_index=True, unique=True)
    bot = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)
    def __str__(self):
        if self.bot == False:
            color = BLACK
        else:
            color = LIGHTGRAY
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.address,
        )

    class Meta:
        verbose_name = 'IP Address'
        verbose_name_plural = 'IP Addresses'

class HostName(models.Model):
    name = models.CharField(verbose_name='Host Name String',max_length=80,db_index=True, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Host Name'

class Path(models.Model):
    search_path = models.CharField(verbose_name='Search Path String',max_length=254,db_index=True, unique=True)
    def __str__(self):
        return self.search_path
    class Meta:
        verbose_name = 'Search Path'

class QueryString(models.Model):
    query_string = models.CharField(verbose_name='Query String',max_length=254,db_index=True, unique=True)
    def __str__(self):
        return self.query_string
    class Meta:
        verbose_name = 'Query String'

class URL(models.Model):
    name = models.CharField(max_length=510,db_index=True, unique=True)

    scheme = models.BooleanField(default=True) # https = True, http = False
    authority = models.ForeignKey(HostName,null=True,blank=True, on_delete=models.SET_NULL)
    port = models.SmallIntegerField(null=True,blank=True)
    path = models.ForeignKey(Path,null=True,blank=True, on_delete=models.SET_NULL)
    query_string = models.ForeignKey(QueryString,null=True,blank=True, on_delete=models.SET_NULL)

    canonical = models.ForeignKey('self', null=True,blank=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'URL'


class MIME(models.Model):
    mime_type_string = models.CharField(verbose_name='MIME Type String',max_length=50,db_index=True, unique=True)
    def __str__(self):
        return self.mime_type_string
    class Meta:
        verbose_name = 'MIME Type'

class Accept(models.Model):
    accept_string = models.CharField(verbose_name='Accept Encoding String',max_length=254,db_index=True, unique=True)
    def __str__(self):
        return self.accept_string
    class Meta:
        verbose_name = 'Accept Encoding'

class Language(models.Model):
    language_string = models.CharField(verbose_name='Language String',max_length=50,db_index=True, unique=True)
    def __str__(self):
        return self.language_string
    class Meta:
        verbose_name = 'Language Encoding'

class Encoding(models.Model):
    encoding_string = models.CharField(verbose_name='Request Encoding String',max_length=50,db_index=True, unique=True)
    def __str__(self):
        return self.encoding_string
    class Meta:
        verbose_name = 'Request Encoding'

class UserAgent(models.Model):
    user_agent_string = models.CharField(verbose_name='User Agent String',max_length=254,db_index=True, unique=True)
    bot = models.BooleanField(default=False)
    def __str__(self):
        if self.bot == False:
            color = BLACK
        else:
            color = LIGHTGRAY
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.user_agent_string,
        )
    class Meta:
        verbose_name = 'User Agent'

class SessionLog(models.Model):
    session_key = models.CharField(max_length=40,null=True,blank=True,db_index=True,unique=True)
    start_time = models.DateTimeField(default=timezone.now,null=True,db_index=True)
    expire_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField(blank=True, null=True)
    bot = models.BooleanField(default=False)
    def __str__(self):
        if self.bot == False:
            color = BLACK
        else:
            color = LIGHTGRAY
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.session_key,
        )
    class Meta:
        verbose_name = 'Session Log'
        verbose_name_plural = 'Sessions'


class AccessLogManager(models.Manager):

    def log(self,response):
        log_data_ready.send(sender=self.__class__, response=response)


class AccessLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now,db_index=True)
    ip = models.ForeignKey(IP,verbose_name="IP Address",on_delete=models.CASCADE)
    def colored_ip(self):
        return self.ip
    colored_ip.short_description = 'IP Address'
    host_name = models.ForeignKey(HostName,null=True,blank=True,related_name="accesslog_host_name",on_delete=models.SET_NULL)
    
    lookup_time = models.FloatField(verbose_name="DNS Lookup Time",default=0,null=True,blank=True)
    ssl_time = models.FloatField(verbose_name="SSL Time",default=0,null=True,blank=True)
    connect_time = models.FloatField(verbose_name="Connect Time",default=0,null=True,blank=True)
    response_time = models.FloatField(verbose_name="Response Time",default=0)
    def colored_response_time(self):
        if self.cached == False:
            color = RED
        else:
            color = BLACK
        return format_html(
            '<span style="color: {};">{:.6}ms</span>',
            color,
            self.response_time,
        )
    colored_response_time.short_description = 'Response Time'

    log_timestamp = models.DateTimeField(auto_now_add=True)
    
    def response_time_ms(self):
        return '%fms' % self.response_time
    response_time_ms.short_description = 'Response time'

    request_url = models.ForeignKey(URL,verbose_name="Request URL",related_name="accesslog_request_url",null=True,blank=True,on_delete=models.SET_NULL)

    status = models.PositiveSmallIntegerField(verbose_name="HTTP Status Code",)
    def colored_request_url(self):
        if self.status in [401,402,403,500]:
            color = RED
        elif self.status in [404]:
            color = ORANGE
        elif self.status in [410]:
            color = PURPLE
        elif self.status in [301,302,308,309]:
            color = BLUE
        elif self.ajax:
            color = GRAY
        else:
            color = BLACK
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.request_url,
        )
    colored_request_url.short_description = 'Request URL'

    protocol = models.CharField(max_length=1,choices=PROTOCOL_CHOICES,default=UNKNOWN)

    method = models.CharField(max_length=1,choices=METHOD_CHOICES,default=GET)

    ajax = models.BooleanField(verbose_name="AJAX Request",default=False)
    preview = models.BooleanField(verbose_name="Preview Request",default=False)
    prefetch = models.BooleanField(verbose_name="Prefetch Request",default=False)

    referer_url = models.ForeignKey(URL, verbose_name="Referer", null=True,blank=True,related_name="accesslog_referer_url",on_delete=models.SET_NULL)

    user_agent = models.ForeignKey(UserAgent,null=True,blank=True,on_delete=models.SET_NULL)
    def colored_user_agent(self):
        return self.user_agent
    colored_user_agent.short_description = 'User Agent'

    request_content_type = models.ForeignKey(MIME,null=True,blank=True,related_name="accesslog_request_content_type",on_delete=models.SET_NULL)
    request_content_length = models.PositiveIntegerField(null=True,blank=True)

    accept_type = models.ForeignKey(Accept,null=True,blank=True,on_delete=models.SET_NULL)
    accept_language = models.ForeignKey(Language,null=True,blank=True,on_delete=models.SET_NULL)
    accept_encoding = models.ForeignKey(Encoding,null=True,blank=True,on_delete=models.SET_NULL)

    response_content_type = models.ForeignKey(MIME,null=True,blank=True,related_name="accesslog_response_content_type",on_delete=models.SET_NULL)

    response_content_length = models.PositiveIntegerField(null=True,blank=True)

    compress = models.CharField(max_length=1,choices=COMPRESSION_CHOICES,default=UNCOMPRESSED)

    def colored_size(self):
        if self.compress == '0':
            color = RED
        elif self.compress == '1':
            color = BLACK
        elif self.compress == '0':
            color = PURPLE
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            self.response_content_length,
        )
    colored_size.short_description = 'Size'


    cached = models.BooleanField(default=False)

    session = models.ForeignKey(Session,null=True,blank=True,on_delete=models.SET_NULL)
    session_log = models.ForeignKey(SessionLog,null=True,blank=True,on_delete=models.SET_NULL)
    def colored_session_log(self):
        return self.session_log
    colored_session_log.short_description = 'Session Log'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,on_delete=models.SET_NULL)

    latitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,null=True,blank=True)

    objects = AccessLogManager()
    
    class Meta:
        ordering = ['-timestamp',]
        verbose_name = 'Access Log'
        verbose_name_plural = 'Accesses'
