from guider.models import City
from solid.tasks import solid_page
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            publisher = solid_page.get_publisher()
            slugs = City.actives.values_list('slug', flat=True)
            for slug in slugs:
                solid_page.apply_async(args=(slug,), publisher=publisher)
        finally:
            publisher.close()
            publisher.connection.close()
