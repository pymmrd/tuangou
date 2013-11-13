from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.views.generic.simple import direct_to_template
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #(r'^static/(?P<path>.+)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT }),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype':'text/plain'}),
    (r'^admin/', include(admin.site.urls)),
    (r'^favicon\.ico$', redirect_to, {'url': settings.MEDIA_URL+'favicon.ico'}), 
    (r'^accounts/', include('accounts.urls')),
    (r'^classify/', include('utils.urls')),
    (r'^wishlist/', include('wishlist.urls')),
    (r'^commerce/', include('commerce.urls')),
    (r'^stats/', include('stats.urls')),
    (r'^search/', include('search.urls')),
    (r'^', include('guider.urls')),
)
handler404 = 'tuangou.views.page_not_found'
handler500 = 'tuangou.views.server_error'
