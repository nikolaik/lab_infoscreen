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

	# static file serving for development 
	# Note: See: http://docs.djangoproject.com/en/dev/howto/static-files/
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/nikk/workspace/lab_infoscreen/static'}),
	#  tvscreen-specific
    (r'^lab/', include('lab_infoscreen.tvscreen.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', include('lab_infoscreen.tvscreen.urls')),
)
