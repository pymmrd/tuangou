import multiprocessing
from optparse import make_option
from guider.models import Category, ReDeal, City
from commerce.models import CustomCategoryDeal 
from django.core.management.base import BaseCommand, CommandError

UNION_SITE = ['wowotuan', 'meituan', 'dazhongdianpin','manzuo', 'luomi', '58tuan', 'juqiwang','pinzhituan', 'sheyingtuan']

CATEGORIES = {'meishitianxia':['meituan', 'dazhongdianpin','ershisiquan','tuanweihui', 'tuangouwang', 'shuangtuan','dazhongdianpin', 'ershisiquan', 'tuanweihui', 'tuangouwang', 'shuangtuan', '58tuan', 'meituan', 'tuangouwang', 'nuomi', 'ershisiquan', 'shuangtuan', 'juqiwang', 'didatuan', 'shuangtuan', 'nuomi', 'dazhongdianpin', 'didatuan', 'nuomi', 'dazhongdianpin', 'didatuan', 'juqiwang', '58tuan', 'meituan', 'nuomi'],
    'xiuxianyule':['meituan', 'dazhongdianpin', 'ershisiquan', '58tuan', 'didatuan', 'nuomi', 'meituan', 'pinzhituan', 'ershisiquan', 'didatuan', 'juqiwang', 'sheyingtuan'],
    'meirongyangsheng':[
        'meituan', 
        'dazhongdianpin', 
        'ershisiquan', 
        'tuanweihui',
        'linglongtuan',
        'pinzhituan',
        'youelwang',
        'weikeshangpin',
        'hongbaotuan',
        'ebaobei',
        'guangpantuan',
        'aotutuan',
        'sifangtuan',
        '58tuan', 
        'pinzhituan', 
        'didatuan', 
        'ershisiquan', 
        'pinzhituan', 
        '58tuan', 
        'pinzhituan', 
        'meituan', 
        'dazhongdianpin'],
    'jiudianlvyou':[
        'dazhongdianpin', 
        '58tuan', 
        'nuomi', 
        'soulvtuan',
        'tuanweihui',
        'pinzhituan',
        'weikeshangpin',
        'hongbaotuan',
        'ebaobei',
        'guangpantuan',
        'aotutuan',
        'sifangtuan',
        'ershisiquan', 
        'lvyoutuan', 
        'didatuan'],
    'huazhuangpin':['dazhongdianpin','77zuo', 'guimituan','yiqimaihaotuan', 'shuangtuan','ershisiquan','didatuan','meituan', '77zuo', 'shuangtuan', 'guimituan', 'diatuan', 'ershiquan', 'guimituan', 'dazhongdianpin', 'shuangtuan', 'gantuanwang','guimituan'],
    'riyongjiaju': ['58tuan'],
    'fuzhuangshipin':['ershisiquan', 'didatuan','guimituan', 'tuangouwang', 'aipintuan','dazhongdianpin', 'guimituan', 'tuangouwang', 'guimituan', 'aipintuan'],
}

def init_category_deal(pk):
    from guider.utils.cache import cache_category_childs_pk
    city = City.objects.get(pk=pk)
    active_deals = ReDeal.nonexpires.filter(division=city).count()
    if active_deals > 0:
        for category in Category.top_level().filter(is_active=True):
            try:
                check_list = []
                childs_pk = cache_category_childs_pk(category.slug)
                sites = CATEGORIES[category.slug]
                for index, site in enumerate(sites):
                    if site == 'A':
                        deals = ReDeal.news.values('pk').filter(division=city, category__pk__in=childs_pk, website__slug__in=UNION_SITE).exclude(pk__in=check_list)
                        if not deals:
                            deals = ReDeal.nonexpires.values('pk').filter(division=city, category__pk__in=childs_pk, website__slug__in=UNION_SITE).exclude(pk__in=check_list).order_by('-pk')
                    else:
                        deals = ReDeal.news.values('pk').filter(division=city, category__pk__in=childs_pk, website__slug=site).exclude(pk__in=check_list)
                        if not deals:
                            deals = ReDeal.nonexpires.values('pk').filter(division=city, category__pk__in=childs_pk, website__slug=site).exclude(pk__in=check_list).order_by('-pk')
                    if deals:
                        deal = deals[0]
                        deal_pk = deal['pk']
                        cdeal = CustomCategoryDeal()
                        cdeal.position = index + 1
                        cdeal.category = category
                        cdeal.deal_id = deal_pk
                        cdeal.division = city
                        cdeal.save()
                        check_list.append(deal_pk)
            except:
                pass

def init(worker):
    CustomCategoryDeal.objects.all().delete()
    from django.db import connection
    connection.close()
    p = multiprocessing.Pool(worker)
    p.map(init_category_deal, City.actives.values_list('pk', flat=True))
    p.close()
    p.join()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--worker', dest='worker', default=2),
    )

    def handle(self, **options):
        worker = int(options.get('worker', 2))
        init(worker)
