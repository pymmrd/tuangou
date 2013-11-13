#from pylib
from datetime import datetime 

#from project
from guider.models import City, Category
from guider.utils.cache import cache_city, cache_category, cache_hot_cities, cache_normal_cities
#from django
from django.db.models import Q

def convert_date(s):
    return datetime.strptime(s, '%Y-%m-%d')

def convert_bool(s):
    flag = False
    if s == '1':
        flag = True
    return flag

def process(request):
    postdata = request.POST.copy()
    site = postdata.get('site', None)
    end_date = convert_date(postdata.get('end_date', None))
    position = postdata.get('position', None)
    h_city = postdata.get('h_city', None)
    o_city = postdata.get('o_city', None)
    cslug= h_city if h_city else o_city
    city = cache_city(cslug)
    priority = int(postdata.get('priority', None))
    category = cache_category(postdata.get('category', None))
    start_date = convert_date(postdata.get('start_date', None))
    return (site, end_date, position, city, priority, category, start_date)

def get_tuple_cities():
    h_cities = cache_hot_cities()
    o_cities = cache_normal_cities()
    return (h_cities, o_cities)

def process_deal(request):
    postdata = request.POST.copy()
    deal_id = int(postdata.get('deal_id', None))
    position = int(postdata.get('position', None))
    h_city = postdata.get('h_city', None)
    o_city = postdata.get('o_city', None)
    cslug= h_city if h_city else o_city
    city = cache_city(cslug)
    category = cache_category(postdata.get('category', None))
    is_active = convert_bool(postdata.get('is_active', None))
    return(deal_id, city, position, category, is_active)

def get_refer_url(request):
    url = ''
    refer = request.META.get('HTTP_REFERER', None)
    if refer:
        url = refer.split('/', 3)[-1]
    return url

def construct_search_query(request):
    h_city = request.GET.get('h_city', None)
    o_city = request.GET.get('o_city', None)
    slug = h_city or o_city or 'beijing'
    city = cache_city(slug)
    queries = [Q(division=city)]
    return queries, city
