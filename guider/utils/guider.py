import re
from django.conf import settings
from tuangou.guider.filters import filter_process
from tuangou.guider.utils.cache import cache_category_deals,\
        cache_district_deals, cache_district_category_deals, cache_feature_deal
from tuangou.guider.utils.common import filter_category_deals, \
                            filter_district_category_deals, district_deals

NORMAL = 1
FEATURE = 2

regx = re.compile(r'http://(?P<domain>.+?\.com).+?')
def parse(link):
    name = ''
    domain = regx.match(link)
    if domain is not None:
        domain_name = domain.group('domain')
        try:
            name = settings.SEARCH_ENGINE[domain_name]
        except KeyError:
            pass
    return name

def get_params(params):
    ordering = price = None
    if params:
        ordering = params.get('ordering', None)
        price = params.get('price', None)
    return (ordering , price)

def _get_district_deals(city, district, page, param):
    from tuangou.guider.utils.common import district_deals
    from tuangou.guider.utils.common import paginate_util
    ordering, price = get_params(param)
    if ordering or price:
        queryset = district_deals(city, district)
        deals = filter_process(queryset, ordering, price)  
        object_list, paginator = paginate_util(deals, page, settings.LIST_PER_PAGE) 
    else:
        object_list, paginator = cache_district_deals(city, district, page)
    return object_list, paginator

def _get_category_deals(city, category, page, param=None):
    from tuangou.guider.utils.common import category_deals
    from tuangou.guider.utils.common import paginate_util
    ordering, price = get_params(param)
    if ordering or price:
        queryset = filter_category_deals(city, category)
        deals = filter_process(queryset, ordering, price)  
        object_list, paginator = paginate_util(deals, page, settings.LIST_PER_PAGE) 
    else:
        object_list, paginator = cache_category_deals(city, category, page)
    return object_list, paginator 

def _get_district_category(city, district, category, page, param):
    from tuangou.guider.utils.common import district_category_deals
    from tuangou.guider.utils.common import paginate_util
    ordering, price = get_params(param)
    if ordering or price:
        queryset = filter_district_category_deals(city, district, category)
        deals = filter_process(queryset, ordering, price)  
        object_list, paginator = paginate_util(deals, page, settings.LIST_PER_PAGE) 
    else:
        object_list, paginator = cache_district_category_deals(city, district, category, page)
    return object_list, paginator

def add_ad_flag(request):
    refer = ''
    ordering = request.GET.get('ordering', None)
    price = request.GET.get('price', None)
    if not price and not ordering:
        agent = request.META.get('HTTP_USER_AGENT', None)
        try:
            refer = settings.SEARCH_ENGINE[agent]
        except KeyError:
            refer = request.META.get('HTTP_REFERER', None)
            refer = parse(refer) if refer  else ''
    return refer

def get_feature_deal(city):
    deal = cache_feature_deal(city)
    return deal

def get_tags(slug):
    banner_site = "tags/banner/%s_site.html" % slug
    seller_chart = "tags/seller/%s_seller_chart.html" % slug
    view_chart = "tags/view/%s_view_chart.html" %  slug
    return banner_site, seller_chart, view_chart

def _rotate_category_index(rows, column,  pageone):
    number = rows * column
    offset  =   number if pageone > number else pageone
    return offset

def get_seo_key(category):
    try:
        seo_key = settings.SEO_KEYWORDS[category.slug]
    except KeyError:
        seo_key = category.title
    return seo_key

def get_page(page):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    return page
