from django.conf.urls.defaults import *

urlpatterns = patterns('utils.views',
    (r'^category/(?P<slug>.+)/$', 'classify_category', {'tmpl': 'admin/classify_category.html'}, 'classify_category'),
    (r'^district/(?P<slug>.+)/$', 'classify_district', {'tmpl': 'admin/classify_district.html'}, 'classify_district'),
    (r'^set-category/$', 'set_category' ),
    (r'^set-parent-district/$', 'set_parent_district'),
    (r'^set-city/$', 'set_city'),
    url(r'^category-none/$', 'none_category', name='none_category'),
)
