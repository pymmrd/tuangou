from django.conf import settings
from django.core.cache import cache
from django.shortcuts import  get_object_or_404
from tuangou.guider.models import City, District, Category

class CacheKeys(object):
    CITY_CACHE = 'city_%s'
    DISTRICT_CACHE = 'district_%s'
    DISTRICTS_CACHE = 'districts_%s'
    CATEGORY_CACHE = 'cat_%s' 
    TOP_CATEGORIES = 'top_cats'
    CATEGORY_CHILDS_CACHE = 'cat_childs_%s'

def get_city_cache(slug):
    cache_key = CacheKeys.CITY_CACHE % slug
    city = cache.get(cache_key, None)
    if city is None:
        city = get_object_or_404(City, slug=slug)
        cache.set(cache_key, city)
    return city

def get_district_cache(city, slug):
    cache_key = CacheKeys.DISTRICT_CACHE % slug
    district = cache.get(cache_key, None)
    if district is None:
        district = get_object_or_404(District, city=city, slug=slug)    
        cache.set(cache_key, district)
    return district

def get_category_cache(slug):
    cache_key = CacheKeys.CATEGORY_CACHE % slug
    category = cache.get(cache_key, None)
    if category is None:
        category = get_object_or_404(Category, slug=slug)
        cache.set(cache_key, category)
    return category

def get_districts_cache(city):
    cache_key = CacheKeys.DISTRICTS_CACHE % city.slug
    districts = cache.get(cache_key, None)
    if districts is None:
        districts = District.actives.values('city__name', 'city__slug', 'name', 
                'slug', 'pk').filter(city=city, parent=None).order_by('city__slug')
        cache.set(cache_key, list(districts))
    return districts

def get_categories_cache():
    cache_key = CacheKeys.TOP_CATEGORIES
    categories = cache.get(cache_key, None)
    if categories is None:
        categories = Category.top_level().order_by('order')
        cache.set(cache_key, list(categories))
    return categories
    
