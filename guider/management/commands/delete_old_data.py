from django.core.management.base import NoArgsCommand
from dateutil import relativedelta
from datetime import datetime, date
from guider.models import ReDeal, Deal_Shop_City_District
from django.core.paginator import Paginator
import os

trash_image_file = 'trash_image_file.txt'

def get_last_month(d):
    return d+relativedelta(months=-1)

def delete_old():
    today = datetime.today()
    #last_month = get_last_month(today)
    deals = ReDeal.objects.filter(end_date__lt=today)
    paginator = Paginator(deals, 1000) 
    pages = paginator.num_pages
    with open(trash_image_file, 'a') as f:
        for page in xrange(1, pages):
            deal_list = paginator.page(page).object_list
            for deal in deal_list:
                image_path = deal.image.__unicode__()
                thumb_path = deal.thumbnail.__unicode__()
                f.write('%s%s%s%s' % (image_path, os.linesep, thumb_path, os.linesep))
                Deal_Shop_City_District.objects.filter(deal_id=deal.id).delete()
                deal.delete()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        delete_old()
