from django.conf.urls.defaults import *

urlpatterns = patterns('union.views',
    (r'^site-pos-changelist/$', 'ad_site_changelist', {'tmpl': 'union/changelist.html'}, 'site-pos-changelist'),
    (r'^site-pos-edit/(?P<object_id>\d+)/$', 'edit_ad_site', {'tmpl': 'union/edit_site.html'}, 'site-pos-edit'),
    (r'^site-pos-add/$', 'add_ad_site', {'tmpl': 'union/add_site.html'}, 'site-pos-add'),
    (r'^site-pos-delete/$', 'delete_ad_site'),
    (r'^ad-changelist/$', 'ad_changelist', {'tmpl': 'union/cdeal_changelist.html'}, 'ad_changelist'),
    (r'^add-deal/$', 'add_deal', {'tmpl': 'union/cdeal_add.html'}, 'add-deal'),
    (r'^edit-deal/(?P<object_id>\d+)/$', 'edit_deal', {'tmpl': 'union/cdeal_edit.html'}, 'edit-deal'),
    (r'^delete-deal/$', 'delete_deal'),
    (r'^search-ad-position/$', 'search_ad_position', {'tmpl': 'union/search_ad_position.html'}, 'search-ad-position'),
    (r'^search-ad-deal/$', 'search_ad_deal', {'tmpl': 'union/search_ad_deal.html'}, 'search-ad-deal'),
    (r'^get-site/$', 'get_site'),
)
