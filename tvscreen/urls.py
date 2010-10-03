from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lab_infoscreen.tvscreen.views',
    # Example:
    # (r'^lab_infoscreen/', include('lab_infoscreen.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'index'),
    (r'^(?P<lab_id>\d+)/$', 'lab'),
    (r'^(?P<lab_id>\d+)/printer/(?P<printer_id>\d+)/$', 'printer_detail'),
)
