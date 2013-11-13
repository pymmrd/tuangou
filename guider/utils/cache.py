import operator
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import  get_object_or_404
from tuangou.guider.models import ReDeal, District, Category, City, FriendLink, Website
from tuangou.commerce.models import CustomCityDeal, CustomCategoryDeal,\
    CustomDistrictDeal, CustomCategoryByDistrict
from tuangou.guider.utils.common import paginate_util

VALUES = ('pk', 'title', 'end_date','image', 
                'start_date', 'deal_url', 'price', 'origin_price', 
                    'discount', 'bought', 'is_ad', 'website__id')
FEATURE = 2
class GuiderCacheKeys(object):
    CITY_CACHE = 'city_%s'
    CATEGORY_CACHE = 'cat_%s'
    CATEGORY_CHILDS = '%s_childs'
    CUSTOM_CATEGORY_ADS = '%s_%s_ads'
    CUSTOM_DISTRICT_ADS = '%s_%s_ads'
    CATEGORY_COUNTER = '%s_%s_counter'
    CATEGORY_CHILDS_PK = 'cat_%s_childs'
    CUSTOM_CATEGORY_AD_IDS = '%s_%s_ids'
    CATEGORY_DEALS = '%s_%s_%s_category'
    CATEGORY_CHILDS_CACHE = 'cat_childs_%s'
    CUSTOM_CATEGORY_DEALS = '%s_%s_custom'
    CATEGORY_DISTRICT_PAGE = '%s_%s_%s_page'
    CUSTOM_DISTRICT_AD_IDS = '%s_%s_dis_ads'
    CUSTOM_DISTRICT_DEALS = '%s_%s_%s_district'
    CUSTOM_DISTRICT_CATEGORY_ADS = '%s_%s_%s_ads'
    CUSTOM_DISTRICT_CATEGORY_DEALS = '%s_%s_%s_ca'
    CUSTOM_DISTRICT_CATEOGY_AD_IDS = '%s_%s_%s_ids' 
    DISTRICT_CHILDS_PK = 'dist_%s_childs'
    DISTRICT_DEALS = '%s_%s_%s_deals' 
    DISTRICT_CACHE = 'district_%s'
    DISTRICTS_CACHE = 'districts_%s'
    DISTRICT_CATEGORY_DEALS = '%s_%s_%s_%s_deals'
    DIVISION_DEALS_PK  = 'division_%s_deals'
    FEATURE_DEAL = 'feature_%s'
    FEATURE_DEAL_ID = 'feature_%s_id'
    TOP_CATEGORIES = 'top_cats'
    FRIEND_LINK = 'friend_links'
    HOT_CITIES = 'hot_cities'
    NORMAL_CITIES = 'normal_cities'
    WEBSITE = 'website_%s'
    SITE_CACHE = 'site_%s'

def cache_domain():
    cache_key = GuiderCacheKeys.SITE_CACHE 
    domain_name = cache.get(cache_key, None)
    if domain_name is None:
        domain_name = Site.objects.values('domain').get(pk=settings.SITE_ID)['domain']
        cache.set(cache_key, domain_name, settings.OBJECT_TIMEOUT) 
    return domain_name

def cache_division_deals(pk):
    if pk == 7:
        div_deals = ReDeal.division.through.objects.values_list('redeal_id', flat=True).filter(city__pk=pk)
    else:
        cache_key = GuiderCacheKeys.DIVISION_DEALS_PK % pk
        div_deals = cache.get(cache_key, [])
        if not div_deals:
            div_deals = ReDeal.division.through.objects.values_list('redeal_id', flat=True).filter(city__pk=pk)
            cache.set(cache_key, list(div_deals), settings.OBJECT_LIST_TIMEOUT)
    return div_deals

def cache_hot_cities():
    VALS = ('name', 'slug')
    cache_key = GuiderCacheKeys.HOT_CITIES 
    cities = cache.get(cache_key, [])
    if not cities :
        cities = City.actives.filter(is_hot=True).values(*VALS).order_by('slug')
        cache.set(cache_key, list(cities), settings.OBJECT_LIST_TIMEOUT)
    return cities

def cache_normal_cities():
    VALS = ('name', 'slug')
    cache_key = GuiderCacheKeys.NORMAL_CITIES 
    cities = cache.get(cache_key, [])
    if not cities:
        cities = City.actives.exclude(is_hot=True).values(*VALS).order_by('slug')
        cache.set(cache_key, list(cities), settings.OBJECT_LIST_TIMEOUT)
    return cities

def cache_category(slug):
    cache_key = GuiderCacheKeys.CATEGORY_CACHE % slug
    category = cache.get(cache_key, None)
    if category is None:
        category = get_object_or_404(Category, slug=slug)
        cache.set(cache_key, category, settings.OBJECT_TIMEOUT)
    return category

def cache_city(slug):
    cache_key = GuiderCacheKeys.CITY_CACHE % slug
    city = cache.get(cache_key, None)
    if city is None:
        city = get_object_or_404(City, slug=slug)
        cache.set(cache_key, city, settings.OBJECT_TIMEOUT)
    return city

def cache_district(city, slug):
    cache_key = GuiderCacheKeys.DISTRICT_CACHE % slug
    district = cache.get(cache_key, None)
    if district is None:
        district = get_object_or_404(District, city=city, slug=slug)    
        cache.set(cache_key, district, settings.OBJECT_TIMEOUT)
    return district

def cache_top_districts(slug):
    cache_key = GuiderCacheKeys.DISTRICTS_CACHE % slug
    districts = cache.get(cache_key, None)
    if districts is None:
        districts = list(District.objects.active().values('city__name', 'city__slug', 'name', 
                'slug', 'pk').filter(city__slug=slug, parent=None).order_by('city__slug'))
        cache.set(cache_key, districts, settings.OBJECTS_TIMEOUT)
    return districts

def cache_district_childs_pk(district):
    cache_key = GuiderCacheKeys.DISTRICT_CHILDS_PK % (district.pk)
    childs = cache.get(cache_key, None)
    if childs is None:
        childs = district.get_active_children_pk(include_self=True)
        cache.set(cache_key, childs, settings.OBJECTS_TIMEOUT)
    return childs

def cache_top_categories():
    cache_key = GuiderCacheKeys.TOP_CATEGORIES
    categories = cache.get(cache_key, None)
    if categories is None:
        categories = list(Category.top_level().order_by('order').values('title', 'slug'))
        cache.set(cache_key, categories, settings.OBJECTS_TIMEOUT)
    return categories

def cache_category_childs(slug):
    cache_key = GuiderCacheKeys.CATEGORY_CHILDS % (slug) 
    category = cache_category(slug)
    childs = cache.get(cache_key, None)
    if childs is None:
        childs = list(category.children.values('title', 'slug'))
        cache.set(cache_key, childs, settings.OBJECTS_TIMEOUT)
    return childs

def cache_category_childs_pk(slug):
    cache_key = GuiderCacheKeys.CATEGORY_CHILDS_PK % (slug) 
    category = cache_category(slug)
    childs = cache.get(cache_key, None)
    if childs is None:
        childs = category.get_active_children_pk(include_self=True)
        cache.set(cache_key, childs, settings.OBJECTS_TIMEOUT)
    return childs

def cache_feature_id(city):
    cache_key = GuiderCacheKeys.FEATURE_DEAL_ID  % city.slug
    deal_id = cache.get(cache_key, None)
    if deal_id is None:
        try:
            deal_id = CustomCityDeal.objects.values_list('deal_id', 
                flat=True).get(is_active=True, division=city, attribute=FEATURE)
        except CustomCityDeal.DoesNotExist:
            pass
        else:
            cache.set(cache_key, deal_id, settings.OBJECT_TIMEOUT)
    return deal_id

def cache_feature_deal(city):
    cache_key = GuiderCacheKeys.FEATURE_DEAL % city.slug
    deal = cache.get(cache_key, None)
    if deal is None:
        deal_id = cache_feature_id(city)
        if deal_id:
            deal = ReDeal.objects.values(*VALUES).get(pk=deal_id)
            cache.set(cache_key, deal, settings.OBJECT_TIMEOUT)
    return deal

def cache_custom_category_ad_ids(city, category, category_pks):
    cache_key = GuiderCacheKeys.CUSTOM_CATEGORY_AD_IDS % (city.slug, category.slug)
    custom_ids = cache.get(cache_key, None)
    if custom_ids is None:
        queries = [Q(division=city), Q(category__pk__in=category_pks)]
        custom_ids = list(CustomCategoryDeal.objects.values_list('deal_id', 
            flat=True).filter(reduce(operator.and_, 
                queries)).exclude(attribute=FEATURE).order_by('position'))
        cache.set(cache_key, custom_ids, settings.OBJECTS_TIMEOUT)
    return custom_ids

def cache_custom_district_ad_ids(city, district):
    cache_key = GuiderCacheKeys.CUSTOM_DISTRICT_AD_IDS % (city.slug, district.slug)
    custom_ids = cache.get(cache_key, [])
    if not custom_ids:
        queries = [Q(division=city), Q(district=district)]
        custom_ids = list(CustomDistrictDeal.objects.values_list('deal_id', 
            flat=True).filter(reduce(operator.and_, queries)).exclude(attribute=FEATURE))
        cache.set(cache_key, custom_ids, settings.OBJECTS_TIMEOUT)
    return custom_ids

def cache_custom_district_category_ad_ids(city, district, category, cpks, dpks):
    cache_key = GuiderCacheKeys.CUSTOM_DISTRICT_CATEOGY_AD_IDS % (city.slug,
                                                district.slug, category.slug )
    custom_ids = cache.get(cache_key, [])
    if not custom_ids:
        queries = [Q(division=city), Q(category__pk__in=cpks), Q(district__pk__in=dpks)]
        custom_ids = list(CustomCategoryByDistrict.objects.values_list('deal_id', 
            flat=True).filter(reduce(operator.and_, 
                    queries)).exclude(attribute=FEATURE).order_by('position'))
        cache.set(cache_key, custom_ids, settings.OBJECTS_TIMEOUT)
    return custom_ids

def _construct_custom_dict(deal):
    return dict(map(lambda x: (x, getattr(deal, x)), VALUES))

def _cache_custom_category_deals(ids):
    ids = ', '.join([str(pk) for pk in ids])
    sql = "select id, id as pk, title, end_date, image, start_date, deal_url, price, origin_price, discount, bought , is_ad, website_id as website__id from redeal where id in (%s) order by instr('%s', id)"
    raw_sql = sql % (ids, ids)
    deals = ReDeal.objects.raw(raw_sql)
    custom_deal = map(_construct_custom_dict, deals)
    return custom_deal

def cache_custom_category_deals(city, category, category_pks):
    cache_key = GuiderCacheKeys.CUSTOM_CATEGORY_ADS % (city.slug, category.slug)
    custom_deals = cache.get(cache_key, [])
    if not custom_deals :
        custom_ids = cache_custom_category_ad_ids(city, category, category_pks)
        if custom_ids:
            #custom_deals = [ReDeal.objects.values(*VALUES).get(pk=pk) for pk in custom_ids]
            custom_deals = _cache_custom_category_deals(custom_ids)
            cache.set(cache_key, custom_deals, settings.OBJECT_LIST_TIMEOUT)
    return custom_deals

def cache_custom_district_deals(city, district):
    cache_key = GuiderCacheKeys.CUSTOM_DISTRICT_ADS % (city.slug, district.slug)
    custom_deals = cache.get(cache_key, [])
    if not custom_deals:
        custom_ids = cache_custom_district_ad_ids(city, district)
        custom_deals = [ReDeal.objects.values(*VALUES).get(pk=pk) for pk in custom_ids]
        cache.set(cache_key, custom_deals, settings.OBJECT_LIST_TIMEOUT)
    return custom_deals

def cache_custom_district_category_deals(city, district, category, cpks, dpks):
    cache_key = GuiderCacheKeys.CUSTOM_DISTRICT_CATEGORY_ADS % (city.slug, 
                                                district.slug, category.slug)
    custom_deals = cache.get(cache_key, [])
    if not custom_deals:
        custom_ids =  cache_custom_district_category_ad_ids(city, 
                                                district, category, cpks, dpks)
        custom_deals = [ReDeal.objects.values(*VALUES).get(pk=pk) for pk in custom_ids]
        cache.set(cache_key, custom_deals, settings.OBJECT_LIST_TIMEOUT)
    return custom_deals

def cache_category_counter(city, category):
    from tuangou.guider.utils.common import category_deals
    cache_key = GuiderCacheKeys.CATEGORY_COUNTER % (city.slug, category.slug) 
    total = cache.get(cache_key, None)
    if total is None:
        deals = category_deals(city, category)
        total = deals.count()
        cache.set(cache_key, total, settings.OBJECT_TIMEOUT)
    return total

def cache_category_deals(city, category, page):
    from tuangou.guider.utils.common import category_deals
    if page <= settings.CACHE_PAGE_NUMBER: 
        cache_key = GuiderCacheKeys.CATEGORY_DEALS % (city.slug, category.slug, page) 
        object_list, num_pages  = cache.get(cache_key, (None, None))
        if not object_list:
            deals = category_deals(city, category)
            object_list, num_pages= paginate_util(deals, page, settings.LIST_PER_PAGE)
            if object_list:
                object_list = _cache_custom_category_deals(object_list)
                cache.set(cache_key, (object_list, num_pages), settings.OBJECT_TUPLE_TIMEOUT)
    else:
        deals = category_deals(city, category)
        object_list, num_pages= paginate_util(deals, page, settings.LIST_PER_PAGE)
        object_list = _cache_custom_category_deals(object_list)
    return object_list, num_pages

def cache_district_category_deals(city, district, category, page):
    from tuangou.guider.utils.common import district_category_deals 
    if page <= settings.CACHE_PAGE_NUMBER: 
        cache_key = GuiderCacheKeys.DISTRICT_CATEGORY_DEALS % (city.slug,
                                        district.slug, category.slug, page)
        object_list, num_pages = cache.get(cache_key, ([], None))
        if not object_list :
            deals = district_category_deals(city, district, category)
            object_list, num_pages = paginate_util(deals, page, settings.LIST_PER_PAGE)
            if object_list:
                object_list = _cache_custom_category_deals(object_list)
                cache.set(cache_key, (object_list, num_pages), settings.OBJECT_TUPLE_TIMEOUT)
    else:
        deals = district_category_deals(city, district, category)
        object_list, num_pages = paginate_util(deals, page, settings.LIST_PER_PAGE)
        object_list = _cache_custom_category_deals(object_list)
    return object_list, num_pages

def cache_district_deals(city, district, page):
    from tuangou.guider.utils.common import district_deals
    if page <= settings.CACHE_PAGE_NUMBER: 
        cache_key = GuiderCacheKeys.DISTRICT_DEALS % (city.slug, district.slug, page)
        object_list, num_pages = cache.get(cache_key, (None, None))
        if object_list is None:
            deals = district_deals(city, district)
            object_list, num_pages= paginate_util(deals, page, settings.LIST_PER_PAGE)
            if object_list:
                object_list = _cache_custom_category_deals(object_list)
                cache.set(cache_key, (object_list, num_pages), settings.OBJECT_TUPLE_TIMEOUT)
    else:
        deals = district_deals(city, district)
        object_list, num_pages= paginate_util(deals, page, settings.LIST_PER_PAGE)
        object_list = _cache_custom_category_deals(object_list)
    return object_list, num_pages

def cache_friend_links():
    values = ('link', 'logo', 'name')
    cache_key = GuiderCacheKeys.FRIEND_LINK 
    object_list = cache.get(cache_key , None)
    if object_list is None:
        links = list(FriendLink.objects.active().values(*values))
        cache.set(cache_key, links, settings.OBJECT_LIST_TIMEOUT)
    return object_list

def cache_website(site_id):
    cache_key = GuiderCacheKeys.WEBSITE % (site_id)
    name = cache.get(cache_key , None)
    if name is None:
        try:
            site = Website.objects.values('name').get(pk=site_id)
        except Website.DoesNotExist:
            pass
        else:
            name = site['name']
            cache.set(cache_key, name, settings.OBJECT_TIMEOUT)
    return name
