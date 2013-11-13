# -*- coding:utf-8 -*-
import operator
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from tuangou.guider.models import ReDeal
from tuangou.commerce.models import CustomCityDeal, MiniCategory, \
    MiniCategory, CarouselAd, MiniItem, JinPinDeal

MINI = 4

class CommerceCacheKeys(object):
    CACHE_MINI_CATS = 'mini_cats'
    CACHE_MINI_CATEGORY = 'mini_%s'
    CACHE_MINI_ITEMS = 'mini_%s_items' 
    CACHE_MINI_JINPIN_DEALS = 'mini_%s_jinpin'
    CACHE_MINI_CUSTOM_DEALS = 'mini_%s_custom'
    CACHE_MINI_CHANNEL_IMG = 'mini_%s_channel'
    CACHE_MINI_CATEGORY_AD_IDS = 'mini_%s_%s_ids'
    CACHE_MINI_CATEGORY_DEALS = '%s_%s_category'

def cache_mini_cats():
    cache_key = CommerceCacheKeys.CACHE_MINI_CATS
    categories = cache.get(cache_key, None)
    if categories is None:
        values = ('name', 'slug', 'url')
        categories = MiniCategory.objects.active().values(*values).order_by('order') 
        counter = categories.count()
        cache.set(cache_key, list(categories), settings.OBJECT_TIMEOUT)
    else:
        counter = len(categories)
    return (categories, counter)

def cache_custom_deals(city):
    cache_key = CommerceCacheKeys.CACHE_MINI_CUSTOM_DEALS % city.slug
    ids = cache.get(cache_key, None)
    if ids is None:
       ids = CustomCityDeal.objects.values_list('deal_id', 
            flat=True).filter(division=city, attribute=MINI).order_by('position') 
       cache.set(cache_key, list(ids), settings.OBJECTS_TIMEOUT)
    return ids 

def cache_jinpin_deals(city):
    cache_key = CommerceCacheKeys.CACHE_MINI_JINPIN_DEALS % city.slug 
    minis = cache.get(cache_key, None)
    if minis is None:
        ids = cache_custom_deals(city)
        values =('pk', 'title', 'end_date','image', 'start_date', 'deal_url', 
                    'price', 'origin_price', 'discount', 'bought', 'website__name')
        minis = [ReDeal.objects.values(*values).get(pk=pk) for pk in ids]
        cache.set(cache_key, list(minis), settings.OBJECTS_TIMEOUT)
    return minis

def cache_mini_category_ad_ids(city, category):
    from tuangou.guider.utils.cache import cache_city
    cache_key = CommerceCacheKeys.CACHE_MINI_CATEGORY_AD_IDS % (city.slug, category.slug)
    custom_ids = cache.get(cache_key, None)
    if custom_ids is None:
        queries = [Q(city=city), Q(category__pk=category.pk)]
        custom_ids = list(JinPinDeal.objects.values_list('deal_id',
            flat=True).filter(reduce(operator.and_, queries)).order_by('position'))
        if not custom_ids:
            quanguo = cache_city('quanguo')
            queries = [Q(city=quanguo), Q(category__pk=category.pk)]
            custom_ids = list(JinPinDeal.objects.values_list('deal_id',
                flat=True).filter(reduce(operator.and_, queries)).order_by('position'))
        cache.set(cache_key, custom_ids, settings.OBJECTS_TIMEOUT)
    return custom_ids

def cache_mini_category_deal(city, category):
    from guider.utils.cache import _cache_custom_category_deals
    cache_key = CommerceCacheKeys.CACHE_MINI_CATEGORY_DEALS % (city.slug, category.slug)
    deals = cache.get(cache_key, None)
    if deals is None:
        ids = cache_mini_category_ad_ids(city, category)
        #values =('pk', 'title', 'end_date','image', 'start_date', 'deal_url', 
        #            'price', 'origin_price', 'discount', 'bought', 'website__name')
        #deals = [ReDeal.objects.values(*values).get(pk=pk) for pk in ids]
        deals = _cache_custom_category_deals(ids)
        cache.set(cache_key, deals, settings.OBJECTS_TIMEOUT)
    return deals

def cache_channel_img(slug):
    cache_key = CommerceCacheKeys.CACHE_MINI_CHANNEL_IMG % slug
    img = cache.get(cache_key, None)
    if img is None:
        category = cache_mini_category(slug)
        values = ('image', 'url')
        try:
            img = CarouselAd.objects.values(*values).get(category=category)
        except CarouselAd.DoesNotExist:
            pass
        else:
            cache.set(cache_key, img)
    return img

def cache_mini_category(slug):
    cache_key = CommerceCacheKeys.CACHE_MINI_CATEGORY % slug
    category = cache.get(cache_key, None)
    if category is None:
        category = MiniCategory.objects.get(slug=slug)
        cache.set(cache_key, category, settings.OBJECT_TIMEOUT)
    return category

def cache_mini_items(slug):
    cache_key = CommerceCacheKeys.CACHE_MINI_ITEMS % slug
    miniitems = cache.get(cache_key, None)
    if miniitems is None:
        category =  cache_mini_category(slug)
        values = ('title', 'image_url', 'url', 'pk')
        miniitems = MiniItem.objects.active(category=category).values(*values)
        cache.set(cache_key, list(miniitems), settings.OBJECTS_TIMEOUT)
    return miniitems
