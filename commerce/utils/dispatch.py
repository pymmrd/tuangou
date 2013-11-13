from random import choice
from django.db.models import Q
from django.conf import settings
from django.template import RequestContext, loader
from datetime import datetime, date, time
from tuangou.utils.location import get_current_city
from tuangou.commerce.models import Advertisement, CityConstrain, DispatchRecord

def gen_response(context, tmpl):
    t = loader.get_template(tmpl) 
    c = RequestContext(context['request'], context)
    response = t.render(c)
    response = response.replace('\n','\r\n')
    return response

def get_active_ads(city):
    ads = Advertisement.objects.active().filter(
            Q(dispatch_city=city)|Q(dispatch_city=None))
    return ads 

def get_distinct_ads(request):
    number = 0
    result_list = []
    city = get_current_city(request)
    mac = request.GET.get('MAC', None)
    dispatched = DispatchRecord.objects.dispatch(mac=mac).values_list('ad__id', flat=True)
    queryset = get_active_ads(city)
    if dispatched:
        queryset = queryset.exclude(id__in=dispatched)
    for ad in queryset:
        if number <= settings.AD_PREFETCH_ONE_TIME:
            try:
                cc = ad.cityconstrain.active().get(division=city)
            except CityConstrain.DoesNotExist:
                flag = check_constrains(ad, city)
            else:
                flag = check_constrains(ad, city, cc)
            if not flag:
                continue
            else:
                result_list.append(ad)
                number += 1
    return result_list

def get_store_ad(request):
    ad = None
    result_list = []
    city = get_current_city(request)
    mac = request.GET.get('MAC', None)
    queryset = get_active_ads(city)
    fetch_type = settings.STORE_FETCH_TYPE
    queryset = queryset.filter(type__in=fetch_type)
    for ad in queryset:
        try:
            cc = ad.cityconstrain.active().get(division=city)
        except CityConstrain.DoesNotExist:
            flag = check_constrains(ad, city)
        else:
            flag = check_constrains(ad, city, cc)
        if flag:
            result_list.append(ad)
    if result_list:
        ad = choice(result_list)
    return ad

def check_constrains(ad, city, cc=None):
    flag = True
    now  = datetime.now()
    start_time = ad.start_time
    expire_time = ad.expire_time
    start_time_per_day = ad.start_time_per_day
    end_time_per_day = ad.expire_time_per_day
    show_times_per_day = ad.show_times_per_day
    show_times = ad.show_times
    if start_time_per_day and now <= start_time_per_day or end_time_per_day and now >= end_time_per_day or start_time and now <= start_time:
        flag = False
    if flag and expire_time and now >= expire_time or show_times and ad.sub_total >= show_times:
        flag = False
        ad.is_active = False
        ad.save()
    if flag and show_times_per_day:
        count = DispatchRecord.objects.dispatch(ad=ad).count()
        if count <= show_times_per_day:
            flag = False
    if flag and cc:
        cc_show_times_per_day = cc.show_times_per_day
        cc_show_times = cc.show_times
        if cc_show_times >= cc.sub_total:
            cc.is_active = False
            cc.save()
            flag = False
        if flag:
            count = DispatchRecord.objects.dispatch(ad=ad, division=city).count()
            if count >= cc_show_times_per_day:
                flag = False
    return flag

def check_validity(request, ad_id):
    mac = request.GET.get('MAC', None)
    city = get_current_city(request)
    ad = Advertisement.objects.get(id=ad_id)
    try:
        cc = ad.cityconstrain.active().get(division=city)
    except CityConstrain.DoesNotExist:
        flag = check_constrains(ad, city)
        if flag:
            increase_show_times(ad, mac, city)
    else:
        flag = check_constrains(ad, city, cc)
        if flag:
            increase_show_times(ad, mac, city, cc)
    return flag

def increase_show_times(ad, mac, city, cc=None):
    ad.sub_total += 1
    total_times = ad.show_times
    if total_times and ad.sub_total >= total_times:
        ad.is_active = False
    ad.save()
    if cc:
        cc.sub_total += 1
        cc_show_times = cc.show_times
        if cc_show_times >= cc.sub_total:
            cc.is_active = False
        cc.save()
    dr = DispatchRecord.objects.create(mac=mac, ad=ad, division=city)
