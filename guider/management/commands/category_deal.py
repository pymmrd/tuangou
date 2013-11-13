import random
from guider.models import Category, ReDeal, City
from commerce.models import CustomCategoryDeal 
from django.core.management.base import NoArgsCommand
from guider.utils.cache import cache_category_childs_pk

meishitianxia = ['meituan', 'dazhongdianpin', 'manzuo', 'didatuan', 'nuomi', '24quan', 'xianzaituan', 'tuangouwang', 'aipintuan', 'ayatuan', 'yeshoutuan', 'juletao', 'bianyituan', 'vctuan', 'beiqingtuan', 'yiqimaihaotuan', 'meiwang',  'youpin360', 'woyetuan', 'guimituan', 'jinzhuangguoji', 'remai', 'jupinyoumei', 'pinzhituan', 'woyetuan', 'yiqigou', 'mengmaiwang', 'beiqintuan']
meirongyangsheng = ['nuomi', '24quan', 'didatuan', 'guimituan', 'juletao', 'meituan', 'xianzaituan', 'bianyituan', 'dazhongdianping', 'ayatuan', 'tuangouwang', 'pinzhituan', 'vctuan', 'yeshoutuan', 'aipintuan', 'manzuo']

def init_meishitianxia_deal():
    check_list = []
    for category in Category.top_level().filter(is_active=True):
        childs_pk = cache_category_childs_pk(category.slug)
        for city in [ 'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'zhengzhou', 'hangzhou'] :
            city = City.objects.get(slug=city)
            #ds = ReDeal.news.filter(division=city, category__pk__in=childs_pk).count()
            position = 1 
            count = 0
            check_list = []
            while count < 48:
                for slug in meishitianxia:
                    deals = ReDeal.news.values('pk', 'website__pk').filter(division=city, category__pk__in=childs_pk, price__range=[100, 200], website__slug=slug)
                    if deals:
                        deal = deals[0]
                        cdeal = CustomCategoryDeal()
                        cdeal.position = position
                        cdeal.category = category
                        cdeal.deal_id =  deal['pk']
                        cdeal.division = city
                        cdeal.save()
                        position +=1 
                        check_list.append(deal['pk'])
                count += 1
            print city.slug,'--->', check_list

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        init_meishitianxia_deal()
