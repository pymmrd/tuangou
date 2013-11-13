import os
import re
import operator
import multiprocessing
from datetime import date
from optparse import make_option
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.template import RequestContext
from django.core.management.base import BaseCommand
from django.contrib.auth.models import AnonymousUser
from django.core.management.base import NoArgsCommand
from tuangou.utils.querysetchain import QuerySetChain
from tuangou.guider.models import City, Category, District, ReDeal, Category
from tuangou.guider.utils.guider import _get_category_deals
from tuangou.commerce.models import CarouselAd, ActivityDeal, CustomCategoryDeal
from tuangou.guider.utils.guider import  get_feature_deal, _rotate_category_index
from guider.utils.cache import cache_category_counter, cache_top_categories, cache_category, cache_top_districts, cache_category_childs 

request = HttpRequest()
request.user = AnonymousUser()
regx1 = re.compile('<python>')
regx2 = re.compile('</python>')

def gen_dest_tmpl(html, filename, path):
    tmpl_dir = os.path.join(settings.TEMPLATE_DIRS[0], path) 
    if not os.path.exists(tmpl_dir):
        os.makedirs(tmpl_dir)
    with open(os.path.join(tmpl_dir, filename), 'w') as f:
        f.write(html)

def solid_carousel(tmpl='dy_tags/carousel.html'):
    carousels = CarouselAd.objects.all()
    html = render_to_string(tmpl, locals(), context_instance=RequestContext(request)).encode(settings.DEFAULT_CHARSET)
    html = regx2.sub('}}', regx1.sub('{{', html))
    gen_dest_tmpl(html, 'carousel.html', 'common') 

def solid_district(city, tmpl="dy_tags/district.html"):
    page = 1
    districts = District.objects.active().values('city__name', 'city__slug', 'name', 'slug', 'pk').filter(city=city, parent=None).order_by('city__slug')
    html = render_to_string(tmpl, locals(), context_instance=RequestContext(request)).encode(settings.DEFAULT_CHARSET)
    path = '%s/%s/' % ('solid', city.slug)
    gen_dest_tmpl(html, 'district.html', path) 

def solid_activity_deals(tmpl="dy_tags/spec_category.html"):
    area = 's' 
    page = 1 
    index = 0 
    rows = 6 
    column = 3 
    number = 60 
    page_flag = 'c'
    values =('pk', 'title', 'end_date','image', 'start_date', 'deal_url', 'price', 'origin_price', 'discount', 'bought', 'is_ad', 'website__name')
    today = date.today()
    MEDIA_URL = settings.MEDIA_URL
    category = Category.objects.get(slug='huodongzhuanqu')
    childs = category.children.values('title', 'slug')
    ids = ActivityDeal.objects.values_list('deal_id', flat=True).filter(is_active=True).order_by('position')
    if ids:
        deals = [ReDeal.objects.values(*values).get(pk=id) for id in ids]
        total = ids.count()
    else:
        deals = ReDeal.objects.values(*values).filter(category=category, is_active=True)
        total = deals.count()
    pageone = number if total > number else total
    offset = _rotate_category_index(rows, column, pageone)
    reserve = pageone - offset
    total_reserve = total - pageone
    result_list = deals[:offset]
    html = render_to_string(tmpl, locals(), context_instance=RequestContext(request)).encode(settings.DEFAULT_CHARSET)
    html = regx2.sub('}}', regx1.sub('{{', html))
    path = 'common'
    gen_dest_tmpl(html, 'spec_category.html', path) 

def solid_feature_deal(city, tmpl="dy_tags/feature_deal.html"):
    page_flag = 'c'
    fdeal = get_feature_deal(city) 
    html = render_to_string(tmpl, locals(), context_instance=RequestContext(request)).encode(settings.DEFAULT_CHARSET)
    html = regx2.sub('}}', regx1.sub('{{', html))
    path = '%s/%s/' % ('solid', city.slug)
    gen_dest_tmpl(html, 'feature_deal.html', path) 

def rotate_category(city, category, tmpl='dy_tags/rotate_category.html'):
    page_flag = 'c'
    index = 0
    page = 1
    MEDIA_URL = settings.MEDIA_URL
    number = settings.LIST_PER_PAGE
    today = date.today()
    try:
        rows, column, area = settings.ROWS_MAP[category.slug]
    except KeyError:
        rows, column, area = [1, 4, None]
    childs = category.children.values('title', 'slug').filter(is_active=True).order_by('order')
    total = cache_category_counter(city, category)
    deals, paginator = _get_category_deals(city, category, page)
    pageone = number if total > number else total
    offset= _rotate_category_index(rows, column, pageone)
    reserve = pageone - offset
    total_reserve = total - pageone
    result_list = deals[:offset]
    html = render_to_string(tmpl, locals(), context_instance=RequestContext(request)).encode(settings.DEFAULT_CHARSET)
    html = regx2.sub('}}', regx1.sub('{{', html))
    path = '%s/%s/%s' % ('solid', city.slug, 'rotate')
    filename = '%s_rotate_category.html' % category.slug
    gen_dest_tmpl(html, filename, path)

def solid(city):
    solid_district(city)
    solid_feature_deal(city)
    for category in Category.top_level().order_by('order'):
        rotate_category(city, category)
