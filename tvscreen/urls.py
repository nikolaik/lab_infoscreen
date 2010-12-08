from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lab_infoscreen.tvscreen.views',
    (r'^$', 'index'),
    (r'^(?P<lab_name>\w+)/$', 'lab'),
    (r'^(?P<lab_name>\w+)/printer/(?P<printer_name>\w+)/$', 'printer_detail'),
    (r'^(?P<lab_name>\w+)/capacity/$', 'lab_capacity'),
)
