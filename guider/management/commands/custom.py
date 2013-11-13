# -*- coding:utf-8 -*-
#from pylib
import operator
import multiprocessing
from optparse import make_option
from datetime import datetime, date, time
from itertools import groupby, izip_longest
#from project
from tuangou.guider.models import City, Website, Deal, ReDeal, \
                                        Deal_Shop_City_District
#from django
from django.conf import settings
from django.core.paginator import Paginator
from django.core.management.base import BaseCommand

def _gen_deals(object_list, city):
    for obj in object_list:
        try:
            try:
                md5sum = obj.md5sum
                deal = ReDeal.objects.get(md5sum=md5sum)
            except ReDeal.DoesNotExist:
                deal = ReDeal()
                deal.md5sum = md5sum
                deal.title = obj.title
                deal.website = obj.website
                deal.start_date = obj.start_date
                deal.end_date = obj.end_date
                deal.deal_url = obj.deal_url
                deal.price = obj.price
                deal.bought = obj.bought
                deal.origin_price = obj.origin_price
                deal.discount = obj.discount
                deal.description = obj.description
                deal.image = obj.image
                deal.thumbnail = obj.thumbnail
                deal.category = obj.category
                deal.save()
                for district in obj.district.all():
                    deal.district.add(district)
                for dsc in Deal_Shop_City_District.objects.filter(deal_id=obj.pk, is_new=True):
                    dsc.deal_id = deal.id
                    dsc.is_new = False
                    dsc.save()
            deal.division.add(city)
        except:
            pass

def _gen_new_deal(id_list, city):
    for ids in izip_longest(*id_list):
        dest_list = list(ids)
        new_deals = Deal.news.filter(pk__in=dest_list)
        _gen_deals(new_deals, city)

def gen_new_deal(city, sites, flag=None, is_famous=False):
    deals_list = []
    for site_id in sites:
        deals = Deal.news.values_list('pk', flat=True).filter(division=city, website__id=site_id)
        count = deals.count()
        if count > 0:
            deals_list.append((list(deals), count))
    if is_famous and deals_list:
        stand_list = []
        red_list = []
        sorted_list = sorted(deals_list, key=operator.itemgetter(1))
        length = len(sorted_list)
        mid = int(length / 2) + 1
        refer = sorted_list[mid-1][1]
        for index, items in enumerate(sorted_list):
            if index <= mid -1:
                stand_list.append(list(items[0]))
            else:
                stand_list.append(list(items[0][:refer]))
                red_list.append(list(items[0][refer:]))
        _gen_new_deal(red_list, city)
        _gen_new_deal(stand_list, city)
    else:
        id_list = [deals for deals, conter in deals_list]
        _gen_new_deal(id_list, city)

def get_ordinary_site(city):
    ordinary_site = Website.actives.values_list('pk', flat=True).filter(opened_city=city, is_famous=False)
    if ordinary_site:
        site_counter = {}
        for site_id in ordinary_site:
            site_counter[site_id] = Deal.news.filter(website__pk=site_id).count()
        sorted_site = sorted(site_counter.items(), key=operator.itemgetter(1), reverse=True)
        site_list = [site_id for site_id, coutner in sorted_site ]
        return paginate(site_list, settings.ORDINARY_SITE_OFFSET)
    return []

def gen_ordinary_new_deal(city):
    or_sites = get_ordinary_site(city)
    for sites,flag in or_sites:
        gen_new_deal(city, sites, flag)

def gen_famous_new_deal(city):
    sites = Website.famouses.values_list('pk', flat=True).filter(opened_city=city).order_by('weight') 
    gen_new_deal(city, sites, is_famous=True)

def gen_deal(pk):
    city = City.objects.get(pk=pk)
    gen_ordinary_new_deal(city)
    gen_famous_new_deal(city)

def paginate(object_list, page_size):
    paginator = Paginator(object_list, page_size)
    pages = paginator.num_pages
    for page in range(1, pages+1):
        object_list = paginator.page(page).object_list
        if page == pages:
            yield (object_list, 1)
        else:
            yield (object_list, 0)

def custom(worker):
    from django.db import connection
    connection.close()
    city_list = paginate(City.actives.values_list('pk', flat=True), 10)
    p = multiprocessing.Pool(worker)
    p.map(gen_deal, [pk for ids, flag in city_list for pk in ids])

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--worker', dest='worker', default=2),)

    def handle(self, **options):
        worker = int(options.get('worker', 2))
        custom(worker)
