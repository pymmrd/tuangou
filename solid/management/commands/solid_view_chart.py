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

def gen_view_chart(tmpl, city):
    today = datetime.combine(date.today(), time(0, 0, 0))
    lastday = today - timedelta(days=1) 
    views = DealView.objects.values_list('pk', 'deal_id').filter(deal__end_date__gte=today, date__gte=lastday, city=city)
    key = operator.itemgetter(1)
    s_views = sorted(views, key=key)
    g_views = groupby(s_views, key=key)
    deals = sorted([(k, len(list(group))) for k, group in g_views], key=key, reverse=True)
    length = len(deals)
    if length < settings.VIEW_CHART:
        deals = deals
    else:
        deals = deals[:settings.VIEW_CHART]
    pre_deals = [deal_id for deal_id, pk in deals]
    object_list = [] 
    for pk in pre_deals:
        object_list.append(ReDeal.objects.values_list('pk', 'title').get(pk=pk))
    if city.slug:
        label = '点击排行榜'
        dest_tmpl ="dy_tags/view/%s_view_chart.html" % city.slug
        html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
        gen_dest_tmpl(html, dest_tmpl)

def solid_chart(tmpl="dy_tags/chart.html"):
    for city in get_city():
        gen_view_chart(tmpl, city)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        solid_chart()
