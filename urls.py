from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^lab_infoscreen/', include('lab_infoscreen.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^lab/', include('lab_infoscreen.tvscreen.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', include('lab_infoscreen.tvscreen.urls')),
)
