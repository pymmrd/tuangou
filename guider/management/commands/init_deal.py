import random
from guider.utils.cache import cache_category_childs_pk, cache_top_categories, cache_category
from tuangou.guider.models import City, Website, ReDeal, Category
from tuangou.commerce.models import CustomCityDeal, CustomCategoryDeal
from django.core.management.base import BaseCommand, NoArgsCommand

"""
def init_feature_deal():
    FEATURE = 2 
    #meishitianxia = ['meituan', 'dazhongdianpin', 'manzuo', 'didatuan', 'nuomi', '24quan', 'xianzaituan', 'tuangouwang', 'aipintuan', 'ayatuan', 'yeshoutuan',  'bianyituan', 'vctuan', 'beiqingtuan', 'yiqimaihaotuan', 'meiwang',  'youpin360', 'woyetuan', 'guimituan', 'jinzhuangguoji', 'remai', 'jupinyoumei', 'pinzhituan', 'woyetuan', 'yiqigou', 'mengmaiwang']
    slug = '55tuan'
    union_site = ['meituan', 'dazhongdianpin', 'manzuo', 'didatuan', 'nuomi', '58tuan']
    deal = None
    category = Category.objects.get(slug='meishitianxia')
    #childs_pk = cache_category_childs_pk(category.slug)
    cdeals = CustomCityDeal.objects.filter(attribute=FEATURE)
    cdeals.delete()
    for city in City.actives.all():
        i = 0 
        deal = None
        while i < len(meishitianxia):
            #deals = ReDeal.news.filter(division=city, website__slug=random.choice(meishitianxia), category__pk__in=childs_pk)
            deals = ReDeal.news.filter(division=city, website__slug=slug)
            if deals:
                deal = deals[0]
                break
            i += 1
        if deal is None:
            while i < len(meishitianxia):
                deals = ReDeal.news.filter(division__slug='quanguo', website__slug=random.choice(meishitianxia))
                if deals:
                    deals = deals[0]
                    break
                i += 1
        if deal :
            cdeal = CustomCityDeal()
            cdeal.deal_id = deal.id
            cdeal.division = city
            cdeal.position = 0
            cdeal.attribute = FEATURE
            cdeal.save()
"""
def init_feature_deal():
    deal = None
    FEATURE = 2 
    slug = 'wowotuan'
    CustomCityDeal.objects.filter(attribute=FEATURE).delete()
    union_site = ['meituan', 'dazhongdianpin', 'manzuo', 'didatuan', 'nuomi', '58tuan']
    for city in City.actives.all():
       # deals = ReDeal.news.filter(division=city, website__slug=slug)
        deals = ReDeal.nonexpires.filter(division=city, website__slug=slug)
        if deals:
            deal = deals[0]
        else:
            for s in union_site:
                #deals = ReDeal.news.filter(division=city, website__slug=s)
                deals = ReDeal.nonexpires.filter(division=city, website__slug=s)
                if deals:
                    deal = deals[0]
        if deal :
            cdeal = CustomCityDeal()
            cdeal.deal_id = deal.id
            cdeal.division = city
            cdeal.position = 0
            cdeal.attribute = FEATURE
            cdeal.save()

def gen_custom_category_deal(city, category, deal, position):
    cdeal = CustomCategoryDeal()
    cdeal.category = category
    cdeal.deal_id = deal.id
    cdeal.division = city
    cdeal.position  = position
    cdeal.save()

def init():
    init_feature_deal()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        init()
