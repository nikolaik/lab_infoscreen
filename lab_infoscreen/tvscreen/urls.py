from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lab_infoscreen.tvscreen.views',
    (r'^$', 'index'),
    (r'^(?P<lab_name>\w+)/$', 'lab'),
    (r'^(?P<lab_name>\w+)/capacity/$', 'lab_capacity'),
    (r'^(?P<lab_name>\w+)/admins/$', 'lab_admins'),
    (r'^(?P<lab_name>\w+)/hours/$', 'lab_hours'),
    (r'^(?P<lab_name>\w+)/printers/$', 'lab_printers'),
    (r'^(?P<lab_name>\w+)/printer/(?P<printer_name>\w+)/$', 'printer_detail'),
)
