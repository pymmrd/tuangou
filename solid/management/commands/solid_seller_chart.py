# -*- coding:utf-8 -*-
import operator
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string
from tuangou.guider.models import ReDeal, City
from tuangou.stats.models import DealView
from itertools import groupby
from solid_utils import gen_dest_tmpl
from datetime import datetime, date, time, timedelta

def get_city():
    for city in City.actives.all():
        yield city

def gen_seller_chart(tmpl, city):
    object_list = ReDeal.nonexpires.values_list('pk', 'title', 'bought').filter(division=city).order_by('-bought')[:settings.SELLER_CHART]
    if city.slug:
        label = '销售排行榜'
        dest_tmpl ="dy_tags/seller/%s_seller_chart.html" % city.slug
        html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
        gen_dest_tmpl(html, dest_tmpl)

def solid_chart(tmpl="dy_tags/chart.html"):
    for city in get_city():
        gen_seller_chart(tmpl, city)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        solid_chart()
