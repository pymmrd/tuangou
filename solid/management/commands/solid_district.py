from django.conf import settings
from solid_utils import gen_dest_tmpl
from tuangou.guider.models import City
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

def gen_district(tmpl):
    for city in City.actives.all():
        if city.districts.all:
            html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
            tmpl = "dy_tags/district/%s_district.html" % city.slug
            gen_dest_tmpl(html, tmpl)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        gen_district(tmpl="dy_tags/district_tag.html")
        

