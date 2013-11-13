from django.conf.urls.defaults import * 

urlpatterns = patterns('stats.views',
    (r'^jump-to/(?P<id>[^/]+)/$', 'stats_jump', {'tmpl': 'stats/stats_jump.html'}, 'stats_jump'),
    (r'^show-audit/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'show_audit', {'tmpl': 'admin/audit/show_audit.html'}, 'audit_show_audit'),
    (r'^show-page-audit/$', 'show_page_audit'), 
    (r'^add-pv-record/$', 'add_pv_record'),
    (r'^get-area-audit/$', 'get_area_audit'),
    (r'^add-click-counter/$', 'add_click_counter'),
    (r'^show-refer-sort/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'show_refer_sort', {'tmpl': 'admin/audit/show_refer_sort.html'}, 'show_refer_sort'),
)
