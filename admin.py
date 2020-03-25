from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import *

# Register your models here.

@admin.register(IP)
class IPAdmin(admin.ModelAdmin):
    list_display = ['id', 'address','bot','latitude','longitude',]
    list_display_links = ['id',]
    list_editable = ['bot',]
    list_filter = ('bot',)
    readonly_fields=('id',)
    search_fields = ['address']
    fieldsets = [
        (None, {'fields': [
            ('address'),
            ('bot'),
            ]
        }),
        ('Geolocation', {'fields': [
            ('latitude'),
            ('longitude'),
            ]
        }),
    ]

@admin.register(HostName)
class HostNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ]
        }),
    ]

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ['id', 'search_path',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['search_path']
    fieldsets = [
        (None, {'fields': [
            ('search_path'),
            ]
        }),
    ]

@admin.register(QueryString)
class QueryStringAdmin(admin.ModelAdmin):
    list_display = ['id', 'query_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['query_string']
    fieldsets = [
        (None, {'fields': [
            ('query_string'),
            ]
        }),
    ]

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ['id','name','canonical','scheme','authority','port','path','query_string']
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['name','canonical',]
    list_filter = ('scheme','authority','port','path','query_string')
    fieldsets = [
        (None, {'fields': [
            ('name'),
            ('canonical'),
            ]
        }),
        ('Parts', {'fields': [
            ('scheme'),
            ('authority'),
            ('port'),
            ('path'),
            ('query_string'),
            ]
        }),
    ]

@admin.register(MIME)
class MIMEAdmin(admin.ModelAdmin):
    list_display = ['id', 'mime_type_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['mime_type_string']
    fieldsets = [
        (None, {'fields': [
            ('mime_type_string'),
            ]
        }),
    ]

@admin.register(Accept)
class AcceptAdmin(admin.ModelAdmin):
    list_display = ['id', 'accept_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['accept_string']
    fieldsets = [
        (None, {'fields': [
            ('accept_string'),
            ]
        }),
    ]

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'language_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['language_string']
    fieldsets = [
        (None, {'fields': [
            ('language_string'),
            ]
        }),
    ]

@admin.register(Encoding)
class EncodingAdmin(admin.ModelAdmin):
    list_display = ['id', 'encoding_string',]
    list_display_links = ['id',]
    readonly_fields=('id',)
    search_fields = ['encoding_string']
    fieldsets = [
        (None, {'fields': [
            ('encoding_string'),
            ]
        }),
    ]

@admin.register(Browser)
class BrowserAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'major_version', 'minor_version',]
    list_display_links = ['id','family', 'major_version', 'minor_version',]
    readonly_fields=('id',)
    search_fields = ['family']
    list_filter = ('family','major_version',)
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('major_version', 'minor_version',),
            ('patch',),
            ]
        }),
    ]

@admin.register(OS)
class OSAdmin(admin.ModelAdmin):
    list_display = ['id', 'family', 'major_version', 'minor_version',]
    list_display_links = ['id','family', 'major_version', 'minor_version',]
    readonly_fields=('id',)
    search_fields = ['family']
    list_filter = ('family','major_version',)
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('major_version', 'minor_version',),
            ('patch','minor_patch'),
            ]
        }),
    ]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot', 'family', 'brand', 'model','mobile','pc','tablet','touch']
    list_display_links = ['id','family', 'brand', 'model',]
    readonly_fields=('id',)
    search_fields = ['family', 'brand', 'model',]
    list_filter = ('family','brand','model','mobile','pc','tablet','touch')
    fieldsets = [
        (None, {'fields': [
            ('family',),
            ('brand', 'model',),
            ('mobile','pc','tablet','touch',),
            ('bot',),
            ]
        }),
    ]

@admin.register(UserAgent)
class UserAgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot', 'browser_link', 'os_link', 'device_link', 'user_agent_string',]
    def browser_link(self, obj):
        if obj.browser:
            url = reverse('admin:analytics_browser_change', args = [obj.browser.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.browser.__str__())
        else:
            html = format_html("-")
        return html
    browser_link.admin_order_field = 'browser'
    browser_link.short_description = 'browser'
    def os_link(self, obj):
        if obj.os:
            url = reverse('admin:analytics_os_change', args = [obj.os.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.os.__str__())
        else:
            html = format_html("-")
        return html
    os_link.admin_order_field = 'os'
    os_link.short_description = 'os'
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:analytics_device_change', args = [obj.device.id])
            html = format_html("<a href='{}'>{}</a>", url, obj.device.__str__())
        else:
            html = format_html("-")
        return html
    device_link.admin_order_field = 'device'
    device_link.short_description = 'device'
    list_display_links = ['id','browser_link', 'os_link', 'device_link', ]
    list_editable = ['bot',]
    list_filter = ('bot',)
    readonly_fields=('id',)
    search_fields = ['user_agent_string']
    fieldsets = [
        (None, {'fields': [
            ('user_agent_string'),
            ('bot'),
            ('browser',),
            ('os',),
            ('device'),
            ]
        }),
    ]

@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'bot','user_id','start_time','expire_time','session_key',]
    list_display_links = ['id',]
    list_editable = ['bot',]
    list_filter = ('bot','user_id','start_time','expire_time')
    readonly_fields=('id',)
    search_fields = ['user_id']
    fieldsets = [
        (None, {'fields': [
            ('session_key'),
            ('bot'),
            ('user_id'),
            ]
        }),
        ('Time', {'fields': [
            ('start_time'),
            ('expire_time'),
            ]
        }),
    ]

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp','colored_ip','colored_response_time','colored_size','colored_request_url','referer_url','colored_user_agent']
    list_display_links = ['timestamp',]
    readonly_fields=('timestamp','user','ip','protocol','request_url','status','method','ajax','preview','prefetch','lookup_time','ssl_time','connect_time','response_time','cached','log_timestamp','referer_url','user_agent','accept_type','accept_language','accept_encoding','response_content_type','response_content_length','compress','session','session_log','latitude','longitude')
    search_fields = [
        'timestamp',
        'ip__address',
        'request_url__name',
        'status',
        'user_agent__user_agent_string',
        'referer_url__name']
    fieldsets = [
        (None, {'fields': [
            ('timestamp','user'),
            ]
        }),
        ('Request', {'fields': [
            ('ip'),
            ('referer_url'),
            ('ajax'),
            ('preview'),
            ('prefetch'),
            ('user_agent'),
            ('accept_type'),
            ('accept_language'),
            ('accept_encoding'),
            ]
        }),
        ('URL', {'fields': [
            ('method'),
            ('request_url'),
            ('status'),
            ('protocol'),
            ]
        }),
        ('Response', {'fields': [
            ('response_content_type'),
            ('response_content_length'),
            ('compress'),
            ]
        }),
        ('Performance', {'fields': [
            ('lookup_time','ssl_time','connect_time'),
            ('response_time'),
            ('cached'),
            ('log_timestamp'),
            ]
        }),
        ('Session', {'fields': [
            ('session'),
            ('session_log'),
            ]
        }),
        ('Geolocation', {'fields': [
            ('latitude'),
            ('longitude'),
            ]
        }),
    ]
