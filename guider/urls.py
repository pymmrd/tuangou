from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('guider.views',
    #(r'^solid/$', 'solid', {'tmpl':'solid/guider/show_city.html'}, 'solid'),
    (r'^index/$', 'index', {'tmpl': 'solid/guider/show_city.html'}, 'index'),
    (r'^link/$',  'show_friend_links', {'tmpl': 'guider/link.html'}, 'link'),
    (r'^download/$', 'download', {'tmpl': 'guider/download.html'}, 'download'),
    (r'^search-city-form/$', 'search_city_form'),
    (r'^open-api/$',    'open_api', {'tmpl': 'guider/open_api.html'}, 'open_api'),
    (r'^add-review/$', 'add_deal_review', {'tmpl':'tags/review_tags.html'}, 'add_review'),
    (r'^get-reserve-deals/$','get_reserve_deals'),
    #(r'^get-spec-deals/$', 'get_spec_reserve_deals'),
    (r'^get-reviews/$', 'get_reviews', {'tmpl': 'tags/review_list.html'}, 'get_reviews'),
    (r'^site-all/$', 'sites', {'tmpl': 'guider/sites.html'}, 'sites'),
    (r'^(?P<slug>[a-zA-Z]+)/$', 'show_city', {'tmpl':'solid/guider/show_city.html'}, 'show_city'),
    (r'^(?P<slug>[^/]+)/category/(?P<cat_slug>[^/]+)/(?P<page>\d+)/$', 'show_category', {'tmpl':'guider/show_category.html'}, 'show_category'),
    (r'^(?P<slug>[^/]+)/district/(?P<dist_slug>[^/]+)/(?P<page>\d+)/$', 'show_district', {'tmpl': 'guider/show_district.html'}, 'show_district'),
    (r'^(?P<slug>[^/]+)/(?P<dist_slug>[^/]+)/(?P<cat_slug>[^/]+)/(?P<page>\d+)/$', 'show_district_category', {'tmpl':'guider/show_district_category.html'}, 'show_district_category'),
    (r'^deal/(?P<deal_id>\d+)/$', 'show_deal_detail', {'tmpl': 'guider/show_deal.html'}, 'show_detail'),
    #(r'^$', 'index', {'tmpl': 'guider/show_city.html'}, 'index'),
    (r'^$', 'index', {'tmpl': 'solid/guider/show_city.html'}, 'index'),
)
