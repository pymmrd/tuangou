# -*- coding:utf-8 -*-
from tuangou.crawls.lashou import *
from tuangou.guider.models import  *
from tuangou.commerce.models import CustomCategoryDeal
from django.core.management.base import NoArgsCommand, CommandError

def save():
    for dist in District.objects.all():
        try:
            dist.save()
        except:
            print dist.pk, dist.name, dist.parent

def cc():
    city = City.objects.get(slug='beijing')
    for category in Category.top_level():
        deals = ReDeal.objects.filter(division=city)[:100]
        for index, deal in enumerate(deals):
            cd = CustomCategoryDeal()
            cd.deal_id = deal.pk
            cd.division = city
            cd.position = index + 1
            cd.category = category
            cd.save()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        site = Website.objects.get(slug='lashouwang')
        for city in City.actives.all():
            for deal in ReDeal.news.filter(division=city, website=site): 
                try:
                    lashou(deal.pk, city.slug, deal.deal_url)
                except:
                    print deal.deal_url
