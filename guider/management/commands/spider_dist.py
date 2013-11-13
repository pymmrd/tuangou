from guider.tasks import crawl
from tuangou.guider.models import Website, City, ReDeal
from django.core.management.base import NoArgsCommand

DISTRICT_SITE = ['manzuo', 'ftuan', 'wowotuan', 'didatuan', 'haotehui', 'lashouwang']
class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            publisher = crawl.get_publisher()
            fields = ('pk', 'deal_url')
            for city in City.actives.all():
                if city.districts.values_list('pk').filter(level=0, is_active=True):
                    for name in DISTRICT_SITE:
                        site = Website.objects.get(slug=name)
                        deals = ReDeal.news.values_list(*fields).filter(website=site, division=city)
                        for pk, url in deals:
                            crawl.apply_async(args=(name, pk, city.slug, url), publisher=publisher)
        finally:
            publisher.close()
            publisher.connection.close()
