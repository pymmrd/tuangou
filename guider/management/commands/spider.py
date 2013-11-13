import os
from optparse import make_option
from datetime import time, datetime
from guider.tasks import gen_deal_record, gen_city_and_api_name
from tuangou.utils import get_lastday
from tuangou.guider.models import Website
from django.core.management.base import NoArgsCommand
from django.conf import settings

def get_site_url():
    sites = Website.actives.order_by('pk')
    for site in sites:
        if not site.api_tags_active:
            yield site.pk, site.deal_api
        else:
            api_list = site.cityapi.all()
            for api in api_list:
                yield site.pk, site.deal_api % api

def get_sites():
    lastday = get_lastday()
    sites = Website.actives.values('pk', 'created_date').filter(created_date__gte=datetime.combine(lastday.date(), time(0, 0, 0))).values_list('pk')
    return sites

def crawler():
    if os.path.exists(settings.RUN_FLAG_FILE):
        os.remove(settings.RUN_FLAG_FILE)
    if os.path.exists(settings.CLOSE_FLAG_FILE):
        os.remove(settings.CLOSE_FLAG_FILE)
    try:
        publisher = gen_city_and_api_name.get_publisher()
        for pk in get_sites():
            gen_city_and_api_name.apply_async(args=(pk,), publisher=publisher)
    finally:
        publisher.close()
        publisher.connection.close()
    try:
        publisher = gen_deal_record.get_publisher()
        for pk, url in get_site_url():
            gen_deal_record.apply_async(args=(pk, url), publisher=publisher)
    finally:
        publisher.close()
        publisher.connection.close()
        
class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        crawler()
