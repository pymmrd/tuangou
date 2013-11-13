from django.core.management.base import BaseCommand, NoArgsCommand
from tuangou.commerce.models import MiniCategory, JinPinDeal 
from tuangou.guider.models import ReDeal, Category, City, Website

INIT_NUMBER = 4

def gen_deal(slug, city):
    from tuangou.guider.utils.cache import cache_category_childs_pk
    pks=ids = []
    childs_pk = cache_category_childs_pk(slug)
    pks = ReDeal.nonexpires.values_list('pk', flat=True).filter(division=city, category__pk__in=childs_pk, website__is_famous=True).order_by('-pk')[:INIT_NUMBER]
    counter = pks.count()
    category = MiniCategory.objects.get(slug=slug)
    if pks and counter < INIT_NUMBER:
        reserve = INIT_NUMBER - counter
        quanguo = City.objects.get(slug='quanguo')
        ids = ReDeal.nonexpires.values_list('pk', flat=True).filter(division=quanguo, category__pk__in=childs_pk, website__is_famous=True).order_by('-pk')[:reserve]
        pks = list(pks)
        pks.extend(list(ids))
    for pk in pks:
        jpdeal = JinPinDeal()
        jpdeal.deal_id = pk
        jpdeal.category = category
        jpdeal.city = city
        jpdeal.save()

def init_jinpin_deal():
    #meishitianxia
    JinPinDeal.objects.all().delete()
    for city in City.actives.all().order_by('slug'):
        gen_deal('meishitianxia', city)
        gen_deal('xiuxianyule', city)
        gen_deal('fuzhuangshipin', city)
        gen_deal('meirongyangsheng', city)
        gen_deal('jiudianlvyou', city)
        gen_deal('huazhuangpin', city)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        init_jinpin_deal()
