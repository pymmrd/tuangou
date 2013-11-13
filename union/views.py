#! -*- coding:utf-8 -*-
#from pylib
import operator
# Create your views here.
#from project
from union.utils.feed import UnionFeed
from union.models import AdSitePosition
from union.utils.union import process, get_tuple_cities, process_deal, \
                get_refer_url, construct_search_query
from commerce.models import CustomCategoryDeal
from guider.utils.cache import cache_top_categories, cache_website 
from tuangou.utils.paginator import paginate_util

#from django
from django.conf import settings
from django.utils import simplejson
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def ad_site_changelist(request, tmpl="union/changelist.html"):
    param = request.GET.copy()
    h_cities, o_cities = get_tuple_cities()
    url = get_refer_url(request)
    if url.startswith('union/site-pos-edit/') or url.startswith('union/site-pos-add/'):
        feed = request.session.get('feed', None)
    objects = AdSitePosition.objects.active() 
    object_list, paginator, page = paginate_util(objects, param, settings.LIST_PER_PAGE)
    p = paginator.page(page)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
def add_ad_site(request, tmpl="union/add_site.html"):
    if request.method == 'POST':
        site, end_date, position, city, priority, category, start_date = process(request)
        adsp = AdSitePosition()
        adsp.priority = priority
        adsp.site = site
        adsp.division = city
        adsp.category = category
        adsp.expire_date = end_date
        adsp.start_date = start_date
        adsp.position = position
        adsp.save()
        url = reverse('site-pos-changelist')
        request.session['feed'] = UnionFeed.ADD_FEED 
        return HttpResponseRedirect(url)
    else:
        h_cities, o_cities = get_tuple_cities()
        categories = cache_top_categories()
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def delete_ad_site(request):
    postdata = request.POST.copy()
    object_id = postdata.get('id', None)
    try:
        object_id = int(object_id)
    except (TypeError, ValueError):
        success = 'False'
    else:
        AdSitePosition.objects.get(pk=object_id).delete()
        success = 'True'
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@staff_member_required
def edit_ad_site(request, object_id, tmpl="union/site_edit.html"):
    object_id = int(object_id)
    categories = cache_top_categories()
    if request.method == 'POST':
        site, end_date, position, city, priority, category, start_date = process(request)
        adsp = get_object_or_404(AdSitePosition, pk=object_id)
        adsp.site = site
        adsp.division = city
        adsp.priority = priority
        adsp.category = category
        adsp.position = position
        adsp.expire_date = end_date
        adsp.start_date = start_date
        adsp.save()
        url = reverse('site-pos-changelist')
        request.session['feed'] = UnionFeed.EDIT_FEED 
        return HttpResponseRedirect(url)
    else:
        h_cities, o_cities = get_tuple_cities()
        adsp = get_object_or_404(AdSitePosition, pk=object_id) 
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
def ad_changelist(request, tmpl="union/cdeal_changelist.html"):
    param = request.GET.copy()
    url = get_refer_url(request)
    if url.startswith('union/add-deal/') or url.startswith('union/edit-deal/'):
        feed = request.session.get('feed', None)
    h_cities, o_cities = get_tuple_cities()
    objects = CustomCategoryDeal.objects.filter(is_active=True)
    object_list, paginator, page = paginate_util(objects, param, settings.LIST_PER_PAGE)
    p = paginator.page(page)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
def add_deal(request, tmpl="union/cdeal_add.html"):
    if request.method == 'POST':
        deal_id, division, position, category, is_active = process_deal(request)
        cdeal = CustomCategoryDeal()
        cdeal.deal_id = deal_id
        cdeal.division = division
        cdeal.position = position
        cdeal.category = category
        cdeal.is_active = is_active
        cdeal.attribute = CustomCategoryDeal.NORMAL
        cdeal.save()
        url = reverse('ad_changelist')
        request.session['feed'] = UnionFeed.ADD_FEED 
        return HttpResponseRedirect(url)
    else:
        categories = cache_top_categories()
        h_cities, o_cities = get_tuple_cities()
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
def edit_deal(request, object_id, tmpl="union/cdeal_edit.html"):
    object_id = int(object_id)
    categories = cache_top_categories()
    if request.method == 'POST':
        deal_id, division, position, category, is_active = process_deal(request)
        cdeal = get_object_or_404(CustomCategoryDeal, pk=object_id)
        cdeal.deal_id = deal_id
        cdeal.division = division
        cdeal.position = position
        cdeal.category = category
        cdeal.is_active = is_active
        cdeal.attribute = CustomCategoryDeal.NORMAL
        cdeal.save()
        url = reverse('ad_changelist')
        request.session['feed'] = UnionFeed.EDIT_FEED 
        return HttpResponseRedirect(url)
    else:
        categories = cache_top_categories()
        h_cities, o_cities = get_tuple_cities()
        cdeal = get_object_or_404(CustomCategoryDeal, pk=object_id)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def delete_deal(request):
    postdata = request.POST.copy()
    object_id = postdata.get('id', None)
    try:
        object_id = int(object_id)
    except (TypeError, ValueError):
        success = 'False'
    else:
        CustomCategoryDeal.objects.get(pk=object_id).delete()
        success = 'True'
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@staff_member_required
def search_ad_position(request, tmpl="union/search_ad_position.html"):
    param = request.GET.copy()
    h_cities, o_cities = get_tuple_cities()
    and_queries, city = construct_search_query(request)
    objects = AdSitePosition.objects.filter(reduce(operator.and_, and_queries))
    object_list, paginator, page = paginate_util(objects, param, settings.LIST_PER_PAGE)
    p = paginator.page(page)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@staff_member_required
def search_ad_deal(request, tmpl="union/search_ad_deal.html"):
    param = request.GET.copy()
    h_cities, o_cities = get_tuple_cities()
    and_queries, city = construct_search_query(request)
    objects = CustomCategoryDeal.objects.filter(reduce(operator.and_, and_queries))
    object_list, paginator, page = paginate_util(objects, param, settings.LIST_PER_PAGE)
    p = paginator.page(page)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
def get_site(request):
    param = request.GET.copy()
    site_id = param.get('site_id', None)
    name = None
    try:
        site_id = int(site_id)
    except (ValueError, TypeError):
        success = 'Fasle'
    else:
        name = cache_website(site_id)
    if name: 
        response = simplejson.dumps({'success':'True', 'name': name})
    else:
        msg = u'没有此站点'
        response = simplejson.dumps({'success':'False', 'msg': msg})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
