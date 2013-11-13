# Create your views here.
# -*- coding:utf-8 -*-
#from pylib
from datetime import datetime, time, date
#from django
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
#from project
from tuangou.utils import set_cookie, app_error_log
from tuangou.utils.paginator import paginate_util
from tuangou.utils.cache import get_city_cache, get_districts_cache
from tuangou.guider.models import ReDeal, Deal_Shop_City_District, Category, City, District

CLASSIFY_PER_PAGE = 100 

@staff_member_required
@app_error_log
def classify_category(request, slug, tmpl="admin/classify_category.html"):
    title = u'编辑分类'
    top_cats = Category.top_level().filter(is_active=True)
    city = get_city_cache(slug=slug)
    categories = []
    for cat in top_cats:
        childs = cat.children.active().values('pk', 'title')
        if childs:
            categories.extend(childs)
        else:
            categories.append({'pk':cat.pk, 'title': cat.title})
    param = request.GET.copy()
    object_list = ReDeal.nonexpires.filter(created_date__gte=datetime.combine(date.today(), 
                                time(0, 0, 0)), division=city).order_by('-pk')
    result_list, paginator, page = paginate_util(object_list, param, CLASSIFY_PER_PAGE)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
@app_error_log
def classify_district(request, slug, tmpl="admin/classify_district.html"):
    title = u'编辑商区'
    param = request.GET.copy()
    city = get_city_cache(slug=slug)
    cities = City.actives.values('pk','name', 'slug').order_by('slug')
    ids = ReDeal.nonexpires.values_list('pk', flat=True).filter(division=city)
    object_list = Deal_Shop_City_District.objects.filter(deal_id__in=ids).order_by('-deal_id')
    result_list, paginator, page = paginate_util(object_list, param, CLASSIFY_PER_PAGE)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
@app_error_log
def set_category(request):
    postdata = request.POST.copy()
    deal_id = postdata.get('deal_id')
    category_id = postdata.get('category_id')
    deal = ReDeal.objects.get(pk=int(deal_id))
    category = Category.objects.get(pk=int(category_id))
    deal.category = category
    deal.save()
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@staff_member_required
@app_error_log
def set_parent_district(request):
    postdata = request.POST.copy()
    obj = int(postdata.get('obj'))
    parent = int(postdata.get('parent'))
    dscd = Deal_Shop_City_District.objects.get(pk=obj)
    deal = ReDeal.objects.get(pk=dscd.deal_id)
    try:
        parent = District.objects.get(pk=parent)
    except District.DoesNotExist:
        pass
    else:
        district = dscd.district
        if district:
            if district.level != 0:
                district.parent = parent
                district.save()
        else:
            district = parent
            district.save()
    deal.district.add(district)
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@staff_member_required
def set_city(request):
    postdata = request.POST.copy()
    obj_id = int(postdata.get('obj_id'))
    city_slug = postdata.get('city_slug')
    dscd = Deal_Shop_City_District.objects.get(pk=obj_id)
    city = get_city_cache(city_slug) 
    districts = get_districts_cache(city)
    html = render_to_string('tags/dist_option.html', locals())
    response = simplejson.dumps({'success':'True', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@staff_member_required
def none_category(request, tmpl='admin/classify_category.html'):
    top_cats = Category.top_level().filter(is_active=True)
    categories = []
    for cat in top_cats:
        childs = cat.children.active().values('pk', 'title')
        if childs:
            categories.extend(childs)
        else:
            categories.append({'pk':cat.pk, 'title': cat.title})
    param = request.GET.copy()
    object_list =  ReDeal.nonexpires.filter(category=None).order_by('-pk') 
    result_list, paginator, page = paginate_util(object_list, param, CLASSIFY_PER_PAGE)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))
