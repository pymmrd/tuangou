import re
import os
from tuangou.guider.models import  *
from django.core.management.base import NoArgsCommand, CommandError

def stat():
    count =0 
    for city in City.actives.all():
        count = ReDeal.news.filter(division=city).count()
        print '%s---->%s    ' % (city.name, count), 
        count += 1
        if count % 10 == 0:
            print ""

def stat_url():
    #for site in Website.objects.all():
    site = Website.objects.get(slug='aibang')
    for city in City.actives.all():
        for deal in ReDeal.news.filter(division=city, website=site):
            print "%s   %s  %s" % (site.name, city.name, deal.deal_url)

def rename():
    regx = re.compile(r'[?&=]')
    aibang = Website.objects.get(slug='aibangtuan')
    deals = ReDeal.news.filter(website=aibang)
    for deal in deals:
        path = deal.image.path.split('/', 3)[-1]
        deal.image = path
        tpath = deal.thumbnail.path.split('/', 3)[-1]
        deal.thumbnail = tpath
        deal.save()
    

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        stat()
        
