# -*- coding:utf-8 -*-
# Create your views here.
#from django
import urllib
from datetime import datetime
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.conf import settings
from django.utils import simplejson
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
#from tuangou
from tuangou.utils import app_error_log 
from tuangou.utils.location import get_current_city
from tuangou.guider.models import ReDeal
from tuangou.utils.paginator import paginate_util
from tuangou.commerce.models import Advertisement, ActivityDeal, StoreList, AppCategory, AppItem
from tuangou.commerce.utils.dispatch import get_distinct_ads, check_validity, get_store_ad, gen_response
from tuangou.commerce.utils.klass import get_review_partition
from tuangou.commerce.utils.commerce import jinping_deal, get_mini_category
from tuangou.commerce.utils.app import gen_app_access_log, get_app_audit_data, gen_app_audit_data

CLASSIFY_PER_PAGE = 100 
@app_error_log
def dispatch_ad(request, tmpl='commerce/dispatch_ad.txt'):
    base = settings.AD_INTERVAL
    ads = get_distinct_ads(request)
    counter = len(ads)
    context = RequestContext(request, {'base':base, 'ads':ads, 'counter':counter})
    response = gen_response(context, tmpl)
    return HttpResponse(response, mimetype ='text/plain')

@app_error_log
def dispatch_store_ad(request, tmpl='commerce/dispatch_store_ad.txt'):
    counter = 1
    ad = get_store_ad(request)
    context = RequestContext(request, {'counter': counter, 'ad':ad})
    response = gen_response(context, tmpl)
    return HttpResponse(response, mimetype ='text/plain')

@app_error_log
def verify_ad(request, ad_id, tmpl="commerce/verify_ad.txt"):
    flag = check_validity(request, int(ad_id))
    context = RequestContext(request, {'flag':flag})
    response = gen_response(context, tmpl) 
    return HttpResponse(response, mimetype='text/plain')
    
@app_error_log
def display_ad(request, ad_id, tmpl="commerce/display_ad.html"):
    ad_id = int(ad_id)
    ad = Advertisement.objects.get(id=ad_id)
    template = ad.template
    if template:
        tmpl = template
    deal = ReDeal.objects.get(pk=ad_id)
    context = RequestContext(request, {'deal':deal})
    return render_to_response(tmpl, context)

@staff_member_required
@app_error_log
def activity_deals(request, tmpl="admin/activity_deal.html"):
    values = ('pk', 'title', 'website__name')
    param = request.GET.copy()
    ids = ActivityDeal.objects.values_list('deal_id', flat=True).filter(is_active=True).order_by('position')
    if ids:
        object_list = [ReDeal.objects.values(*values).get(pk=id) for id in ids]
    else:
        slug = 'huodongzhuanqu'
        object_list = ReDeal.objects.values(*values).filter(category__slug='huodongzhuanqu', is_active=True)
    result_list, paginator, page = paginate_util(object_list, param, CLASSIFY_PER_PAGE)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
@app_error_log
def set_activity_position(request):
    postdata = request.POST.copy()
    deal_id = postdata.get('deal_id', None)
    position = postdata.get('position', None)
    try:
        ad = ActivityDeal.objects.get(deal_id=int(deal_id))
    except ActivityDeal.DoesNotExist:
        ad  = ActivityDeal()
        ad.deal_id = int(deal_id)
    ad.position = int(position)
    ad.save()
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
def get_store_list(request, tmpl="commerce/store_list.txt"):
    count = 0
    storelist = StoreList.objects.active().values('domain')
    if storelist:
        count = storelist.count()
    context = RequestContext(request, {'count':count, 'storelist': storelist})
    response = gen_response(context, tmpl)
    return HttpResponse(response, mimetype ='text/plain')

def get_mini(request, tmpl='commerce/dispatch_mini.txt'):
    context = RequestContext(request)
    response = gen_response(context, tmpl)
    return HttpResponse(response, mimetype ='text/plain')

def verify_mini(request, tmpl='commerce/verify_mini.html'):
    flag = True
    context = RequestContext(request, {'flag':flag})
    response = gen_response(context, tmpl) 
    return HttpResponse(response, mimetype='text/plain')

@app_error_log
def show_mini(request, tmpl='commerce/show_mini.html'):
    city = get_current_city(request)
    categories, counter = get_mini_category()
    context = RequestContext(request, {'city':city, 'categories':categories, 'counter':counter})
    return render_to_response(tmpl, context)

@csrf_exempt
def review(request, tmpl="commerce/review.html"):
    if request.method == 'POST':
        if request.user.is_authenticated():
            postdata = request.POST.copy()
            comment = postdata.get('comment', None)
            model = get_review_partition(request.user.id)
            new  = model(comment=comment, user=request.user, ip_address=request.META.get('REMOTE_ADDR', None))
            new.save()
            response = simplejson.dumps({'success':'True'})
        else:
            response = simplejson.dumps({'success':'False'})
        return HttpResponse(response, content_type='application/javascript; charset=utf-8')
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@app_error_log
def show_my_collection(request, tmpl='commerce/show_my_collection.html'):
    collection_list = []
    param = request.GET.copy()
    vcode = param.get('vcode', None)
    items = param.get('items', None)
    toggle = param.get('toggle', None)
    category = get_object_or_404(AppCategory, vcode=vcode)
    if toggle:
        flag = True
    if items:
        items = map(int, items.split(','))
        collection_list = AppItem.objects.filter(category=category, pk__in=items)
    recommand_list = AppItem.objects.active().filter(category=category)
    recommand_list, paginator, page = paginate_util(recommand_list, param, settings.APP_LIST_PER_PAGE)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@app_error_log
def recommand_apps(request, tmpl='tags/commerce/app_object_tag.html'):
    param = request.GET.copy()
    vcode = param.get('vcode', None)
    category = get_object_or_404(AppCategory, vcode=vcode)
    object_list = AppItem.objects.filter(category=category)
    context = RequestContext(request, {'vcode': vcode, 'object_list': object_list})
    html = render_to_string(tmpl, context)
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

def share_to_community(request):
    url = None
    param = request.GET.copy()
    community = param.get('community', None)
    if community == 'sina':
        url = "http://v.t.sina.com.cn/share/share.php?url=http://www.laidiantuan.com&title=%40%E6%9D%A5%E7%82%B9%E5%9B%A2%23%E6%9C%80%E5%A5%BD%E7%9A%84%E4%B8%AD%E5%9B%BD%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%2C%E7%BE%8E%E5%9B%A2%2C%E7%B3%AF%E7%B1%B3%E7%AD%89%E6%AF%8F%E6%97%A5%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%AF%BC%E8%88%AA!%E6%B1%87%E9%9B%86%E5%8C%97%E4%BA%AC%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E4%B8%8A%E6%B5%B7%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E5%92%8C%E5%8C%85%E6%8B%AC%E5%B9%BF%E5%B7%9E%2C%E6%B7%B1%E5%9C%B3%2C%E5%8D%97%E4%BA%AC%2C%E6%9D%AD%E5%B7%9E%2C%E6%88%90%E9%83%BD%2C%E9%9D%92%E5%B2%9B%2C%E8%A5%BF%E5%AE%89%E7%AD%89%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%E5%92%8C%E5%9B%A2%E8%B4%AD%E5%AF%BC%E8%88%AA"
    elif community == 'qq':
        url = "http://share.v.t.qq.com/index.php?c=share&a=index&title=%40%E6%9D%A5%E7%82%B9%E5%9B%A2%23%E6%9C%80%E5%A5%BD%E7%9A%84%E4%B8%AD%E5%9B%BD%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%2C%E7%BE%8E%E5%9B%A2%2C%E7%B3%AF%E7%B1%B3%E7%AD%89%E6%AF%8F%E6%97%A5%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%AF%BC%E8%88%AA!%E6%B1%87%E9%9B%86%E5%8C%97%E4%BA%AC%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E4%B8%8A%E6%B5%B7%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E5%92%8C%E5%8C%85%E6%8B%AC%E5%B9%BF%E5%B7%9E%2C%E6%B7%B1%E5%9C%B3%2C%E5%8D%97%E4%BA%AC%2C%E6%9D%AD%E5%B7%9E%2C%E6%88%90%E9%83%BD%2C%E9%9D%92%E5%B2%9B%2C%E8%A5%BF%E5%AE%89%E7%AD%89%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%E5%92%8C%E5%9B%A2%E8%B4%AD%E5%AF%BC%E8%88%AA&url=http://www.laidiantuan.com&site=http://www.laidiantuan.com"
    elif community == 'qqzone':
        url = "http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=http%3A%2F%2Fwww.laidiantuan.com"
    elif community == '163':
        url = "http://t.163.com/article/user/checkLogin.do?link=http://www.laidiantuan.com/&source=%E6%9D%A5%E7%82%B9%E5%9B%A2&info=%E3%80%90%E6%9D%A5%E7%82%B9%E5%9B%A2%E3%80%91%23%E6%9C%80%E5%A5%BD%E7%9A%84%E4%B8%AD%E5%9B%BD%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%2C%E7%BE%8E%E5%9B%A2%2C%E7%B3%AF%E7%B1%B3%E7%AD%89%E6%AF%8F%E6%97%A5%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%AF%BC%E8%88%AA!%E6%B1%87%E9%9B%86%E5%8C%97%E4%BA%AC%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E4%B8%8A%E6%B5%B7%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E5%92%8C%E5%8C%85%E6%8B%AC%E5%B9%BF%E5%B7%9E%2C%E6%B7%B1%E5%9C%B3%2C%E5%8D%97%E4%BA%AC%2C%E6%9D%AD%E5%B7%9E%2C%E6%88%90%E9%83%BD%2C%E9%9D%92%E5%B2%9B%2C%E8%A5%BF%E5%AE%89%E7%AD%89%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%E5%92%8C%E5%9B%A2%E8%B4%AD%E5%AF%BC%E8%88%AA%20http%3A%2F%2Fwww.laidiantuan.com&1326184436180"
    elif community == 'douban':
        url = "http://shuo.douban.com/!service/share?image=&href=http%3A%2F%2Fwww.laidiantuan.com&name=%E3%80%90%E6%9D%A5%E7%82%B9%E5%9B%A2%E3%80%91%E6%9C%80%E5%A5%BD%E7%9A%84%E4%B8%AD%E5%9B%BD%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%2C%E7%BE%8E%E5%9B%A2%2C%E7%B3%AF%E7%B1%B3%E7%AD%89%E6%AF%8F%E6%97%A5%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%AF%BC%E8%88%AA!%E6%B1%87%E9%9B%86%E5%8C%97%E4%BA%AC%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E4%B8%8A%E6%B5%B7%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E5%92%8C%E5%8C%85%E6%8B%AC%E5%B9%BF%E5%B7%9E%2C%E6%B7%B1%E5%9C%B3%2C%E5%8D%97%E4%BA%AC%2C%E6%9D%AD%E5%B7%9E%2C%E6%88%90%E9%83%BD%2C%E9%9D%92%E5%B2%9B%2C%E8%A5%BF%E5%AE%89%E7%AD%89%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%E5%92%8C%E5%9B%A2%E8%B4%AD%E5%AF%BC%E8%88%AAhttp%3A%2F%2Fwww.laidiantuan.com"
    else:
        url = "http://share.renren.com/share/buttonshare.do?link=http://www.laidiantuan.com&title=%E3%80%90%E6%9D%A5%E7%82%B9%E5%9B%A2%E3%80%91%E6%9C%80%E5%A5%BD%E7%9A%84%E4%B8%AD%E5%9B%BD%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%2C%E7%BE%8E%E5%9B%A2%2C%E7%B3%AF%E7%B1%B3%E7%AD%89%E6%AF%8F%E6%97%A5%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%AF%BC%E8%88%AA!%E6%B1%87%E9%9B%86%E5%8C%97%E4%BA%AC%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E4%B8%8A%E6%B5%B7%E5%9B%A2%E8%B4%AD%E7%BD%91%2C%E5%92%8C%E5%8C%85%E6%8B%AC%E5%B9%BF%E5%B7%9E%2C%E6%B7%B1%E5%9C%B3%2C%E5%8D%97%E4%BA%AC%2C%E6%9D%AD%E5%B7%9E%2C%E6%88%90%E9%83%BD%2C%E9%9D%92%E5%B2%9B%2C%E8%A5%BF%E5%AE%89%E7%AD%89%E7%9A%84%E5%9B%A2%E8%B4%AD%E7%BD%91%E7%AB%99%E5%A4%A7%E5%85%A8%E5%92%8C%E5%9B%A2%E8%B4%AD%E5%AF%BC%E8%88%AAhttp%3A%2F%2Fwww.laidiantuan.com"
    return HttpResponseRedirect(url)

def show_app(request, app_id, tmpl="commerce/show_app.html"):
    app = get_object_or_404(AppItem, pk=int(app_id))
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def record_app_access(request):
    param = request.GET.copy()
    url = param.get('url', None)
    gen_app_access_log(request, url)
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
def record_app_click(request):
    postdata = request.POST.copy()
    vcode = postdata.get('vcode', None)
    if vcode:
        position = postdata.get('position', None)
        gen_app_audit_data(vcode, position)
        response = simplejson.dumps({'success':'True'})
    else:
        response = simplejson.dumps({'success': 'False'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

def show_app_click_audit(request, year, month, day, tmpl='admin/audit/show_app_click_audit.html'):
    vcode = '01'
    d = datetime(int(year), int(month), int(day))
    title = '%s-%s-%s App点击统计' % (d.strftime('%Y'), d.strftime('%m'), d.strftime('%d'))
    pick_data = get_app_audit_data(vcode, d)
    items = sorted(pick_data.iteritems())
    total = sum(pick_data.itervalues())
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
def show_app_audit_from_ajax(request, tmpl='admin/tags/app_chart.html'):
    postdata = request.POST.copy()
    year = postdata.get('year', None)
    month = postdata.get('month', None)
    day = postdata.get('day', None)
    vcode = postdata.get('vcode', None)
    d = datetime(int(year), int(month), int(day))
    pick_data = get_app_audit_data(vcode, d)
    items = sorted(pick_data.iteritems())
    total = sum(pick_data.itervalues())
    html = render_to_string(tmpl, locals())
    response = simplejson.dumps({'success': 'True', 'html': html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
def record_mini_click(request):
    postdata = request.POST.copy()
    category = postdata.get('category', None)
    if category:
        position = postdata.get('position', None)
        gen_app_audit_data(category, position)
        response = simplejson.dumps({'success':'True'})
    else:
        response = simplejson.dumps({'success': 'False'})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

def show_mini_click_audit(request, year, month, day, tmpl='admin/audit/show_mini_click_audit.html'):
    category = 'meishitianxia'
    categories, counter = get_mini_category()
    d = datetime(int(year), int(month), int(day))
    title = '%s-%s-%s mini点击统计' % (d.strftime('%Y'), d.strftime('%m'), d.strftime('%d'))
    pick_data = get_app_audit_data(category, d)
    items = sorted(pick_data.iteritems())
    total = sum(pick_data.itervalues())
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))
