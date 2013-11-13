from guider.tasks import classify
from tuangou.guider.models import ReDeal
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            publisher = classify.get_publisher()
            deals = ReDeal.news.values_list('pk', flat=True)
            for pk in deals:
                classify.apply_async(args=(pk,), publisher=publisher)
        finally:
            publisher.close()
            publisher.connection.close()
