#from pylib
import operator
#frm django
from django.db.models import Q
from django.shortcuts import  get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from project
from tuangou.utils.querysetchain import QuerySetChain
from tuangou.guider.models import ReDeal

VALUES = ('pk', 'title', 'end_date','image', 'start_date', 
            'deal_url', 'price', 'origin_price', 'discount', 
            'bought', 'is_ad', 'website__id')
FEATURE = 2

def paginate_util(obj_list, page, page_size):
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    #generate the paginator object
    paginator = Paginator(obj_list, page_size)
    try:
        result_list  = paginator.page(page).object_list
    except (InvalidPage, EmptyPage):
        result_list = paginator.page(1).object_list
    return result_list, paginator.num_pages

def retrieve_division_deals(pk):
    from tuangou.guider.utils.cache import cache_division_deals
    return cache_division_deals(pk)
    #return ReDeal.division.through.objects.values_list('redeal_id').filter(city__pk=pk)

def category_deals(city, category):
    from tuangou.guider.utils.cache import cache_city
    from tuangou.guider.utils.cache import cache_category_childs_pk
    from tuangou.guider.utils.cache import cache_custom_category_deals
    from tuangou.guider.utils.cache import cache_custom_category_ad_ids
    category_pks = cache_category_childs_pk(category.slug)
    rc_ids = retrieve_division_deals(city.pk)
    queries = [Q(pk__in=rc_ids), Q(category__pk__in=category_pks)]
    #custom_deals = cache_custom_category_deals(city, 
    #                                        category, category_pks)
    custom_ids = cache_custom_category_ad_ids(city,
                                            category, category_pks)
    city_ids = ReDeal.nonexpires.values_list('id', flat=True).filter(reduce(operator.and_, 
                                queries)).exclude(pk__in=custom_ids).order_by('-pk')
    quanguo = cache_city(slug='quanguo')
    qrc_ids = retrieve_division_deals(quanguo.pk)
    queries = [Q(pk__in=qrc_ids), Q(category__pk__in=category_pks)]
    qg_ids = ReDeal.nonexpires.values_list('id', flat=True).filter(reduce(operator.and_, 
                                queries)).exclude(pk__in=custom_ids).order_by('-pk')
    deals = QuerySetChain(custom_ids, city_ids, qg_ids) 
    return deals

def district_category_deals(city, district, category):
    from tuangou.guider.utils.cache import cache_category_childs_pk
    from tuangou.guider.utils.cache import cache_district_childs_pk
    from tuangou.guider.utils.cache import cache_custom_district_category_deals
    from tuangou.guider.utils.cache import cache_custom_district_category_ad_ids
    rc_ids = retrieve_division_deals(city.pk)
    category_pks = cache_category_childs_pk(category.slug)
    district_pks = cache_district_childs_pk(district)
    queries = [Q(pk__in=rc_ids), Q(category__pk__in=category_pks),
                                        Q(district__pk__in=district_pks)]
    custom_ids = cache_custom_district_category_ad_ids(city, district, 
                                        category, category_pks, district_pks)
    #custom_deals = cache_custom_district_category_deals(city, district, 
    #                                    category, category_pks, district_pks)
    dc_ids = ReDeal.nonexpires.values_list('id', flat=True).filter(reduce(operator.and_, 
                            queries)).exclude(pk__in=custom_ids).order_by('-pk')
    deals = QuerySetChain(custom_ids, dc_ids)
    return deals

def district_deals(city, district):
    from tuangou.guider.utils.cache import cache_district_childs_pk
    district_pks = cache_district_childs_pk(district) 
    rc_ids = retrieve_division_deals(city.pk)
    queries = [Q(pk__in=rc_ids), Q(district__pk__in=district_pks)]
    deals = ReDeal.nonexpires.values_list('id', flat=True).filter(
                    reduce(operator.and_, queries)).order_by('-pk')
    return deals

def filter_category_deals(city, category):
    from tuangou.guider.utils.cache import cache_city
    from tuangou.guider.utils.cache import cache_category_childs_pk
    from tuangou.guider.utils.cache import cache_custom_category_deals
    from tuangou.guider.utils.cache import cache_custom_category_ad_ids
    quanguo = cache_city(slug='quanguo')
    rc_ids = retrieve_division_deals(city.pk)
    qrc_ids = retrieve_division_deals(quanguo.pk)
    category_pks = cache_category_childs_pk(category.slug)
    queries = [Q(pk__in=rc_ids)|Q(pk__in=qrc_ids), Q(category__pk__in=category_pks)]
    custom_deals = cache_custom_category_deals(city, 
                                        category, category_pks)
    custom_ids = cache_custom_category_ad_ids(city, category,
                                                    category_pks)
    deals = ReDeal.nonexpires.values(*VALUES).filter(reduce(
                operator.and_, queries)).exclude(pk__in=custom_ids)
    return deals

def filter_district_category_deals(city, district, category):
    from tuangou.guider.utils.cache import cache_city
    from tuangou.guider.utils.cache import cache_category_childs_pk
    from tuangou.guider.utils.cache import cache_district_childs_pk
    from tuangou.guider.utils.cache import cache_custom_district_category_deals
    from tuangou.guider.utils.cache import cache_custom_district_category_ad_ids
    rc_ids = retrieve_division_deals(city.pk)
    category_pks = cache_category_childs_pk(category.slug)
    district_pks = cache_district_childs_pk(district)
    custom_ids = cache_custom_district_category_ad_ids(city, district, 
                                        category, category_pks, district_pks)
    custom_deals = cache_custom_district_category_deals(city, district, 
                                        category, category_pks, district_pks)
    queries = [Q(pk__in=rc_ids), Q(category__pk__in=category_pks), 
                                            Q(district__pk__in=district_pks)]
    deals = ReDeal.nonexpires.values(*VALUES).filter(reduce(
                            operator.and_, queries)).exclude(pk__in=custom_ids)
    return deals
