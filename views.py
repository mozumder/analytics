from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse, JsonResponse, HttpResponseNotFound
from .models import AccessLog
from .signals import *

# Create your views here.

class AnalyticResponseBase():

    def __init__(self, request=None, slug=None, id=None, cached=False,*args, **kwargs):
        self.request = request
        self.slug = slug
        self.id = id
        self.cached = cached
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def close(self):
        super().close()
        log_response.send(sender=AccessLog.objects.__class__, response=self)


class AnalyticResponse(AnalyticResponseBase, HttpResponse):

    def __init__(self, request=None, slug=None, id=None, cached=None, content=b'', content_type=None, status=200, reason=None, charset=None):
        super().__init__(request, slug, id, cached, content, content_type, status, reason, charset)

class HTMLAnalyticResponse(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=200, reason=None, charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

class StreamingHTMLAnalyticResponse(AnalyticResponseBase, StreamingHttpResponse):

    def __init__(self, streaming_content=(), status=200, reason=None, charset=None, request=None, slug=None, id=None, pageKey=None):
        self.pageKey = pageKey
        super().__init__(request, slug, id, cached=False, streaming_content=streaming_content, status=status, reason=reason, charset=charset)

class JSONAnalyticResponse(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=200, reason=None, charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, "application/json", status, reason, charset)


class AnalyticsHttpResponseNotFound(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=404, reason='Not Found', charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

class AnalyticsHttpResponseBadRequest(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=400, reason='Bad Request', charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

class AnalyticsHttpResponseForbidden(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=403, reason='Forbidden', charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

class AnalyticsHttpResponseGone(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=410, reason='Gone', charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

class AnalyticsHttpResponseServerError(AnalyticResponseBase, HttpResponse):

    def __init__(self, content=b'', status=500, reason='Server Error', charset=None, request=None, slug=None, id=None, cached=False):
        self.length = len(content)
        super().__init__(request, slug, id, cached, content, status=status, reason=reason, charset=charset)

