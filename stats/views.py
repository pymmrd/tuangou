# Create your views here.
# -*- coding:utf-8 -*-
import os
import re
import marshal
from datetime import datetime
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
#from project
from tuangou.utils import app_error_log
from tuangou.commerce.models import CarouselAd
from tuangou.guider.models import Website, ReDeal
from tuangou.stats.utils.audit_site import gen_audit_data, get_and_check_pickfile, \
    get_normal_pickfile, get_position_pickfile, get_sub_pv_uv, get_page_audit, click_counter, \
    get_click_file

@app_error_log
def stats_jump(request, id, tmpl='stats/stats_jump.html'):
    param = request.GET.copy()
    area = param.get('area', None)
    r = param.get('r', None)
    ca = param.get('ca', None)
    try:
        id = int(id)
    except (ValueError, TypeError):
        id = int(id.split('-')[-1])
        website = Website.objects.get(pk=id)
        name = website.name
        domain =url = website.url
    else:
        if ca:
            area = "c_a"
            ca = CarouselAd.objects.get(pk=id)
            name = ca.title
            domain=url=ca.url
        else:
            deal = ReDeal.objects.get(pk=id)
            name = deal.website.name
            domain = deal.website.url
            url = deal.deal_url
    if area:
        gen_audit_data(request, name, id, area, r, flag='uv')
    return HttpResponseRedirect(url)

@csrf_exempt
@app_error_log
def add_pv_record(request):
    success = 'True'
    postdata = request.POST.copy()
    name = postdata.get('domain', None)
    refer = postdata.get('refer', None)
    area = postdata.get('area', None)
    id = postdata.get('id', None)
    gen_audit_data(request, name, id, area, refer, flag='pv')
    click_counter()
    response = simplejson.dumps({'success':success})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

"""
@csrf_exempt
@app_error_log
@staff_member_required
def show_audit(request, year, month, day, tmpl="admin/audit/show_audit.html"):
    area = bl = 'b'
    page = 'city'
    uv_dict = pv_dict = {}
    sub_pv = sub_uv = 0
    pick_name = '%s.pk' % bl
    title = '%s-%s-%s广告统计' % (year, month, day)
    d = datetime(int(year), int(month), int(day))
    path, flag = get_and_check_pickfile(d, pick_name, bl, page)
    total_pv = total_uv = 0
    if flag and os.path.exists(path):
        uv_dict = pv_dict = get_normal_pickfile(path)
        total_pv, total_uv = sub_pv, sub_uv = get_sub_pv_uv(pv_dict, uv_dict)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))
"""
def show_audit(request, year, month, day, tmpl='admin/audit/show_audit.html'):
    c_total = 0
    page = 'city'
    title = '%s-%s-%s广告统计' % (year, month, day)
    d = datetime(int(year), int(month), int(day))
    click_file = get_click_file(d)
    with open(click_file, 'r') as f:
        try:
            c_total = int(f.readline().strip()) 
        except (ValueError, TypeError):
            c_total = 0
    items, total = get_page_audit(page, d)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def show_page_audit(request, tmpl="admin/tags/chart_tag.html"):
    postdata = request.POST.copy()
    year = postdata.get('year', None)
    month = postdata.get('month', None)
    day = postdata.get('day', None)
    page = postdata.get('page', None)
    d = datetime(int(year), int(month), int(day))
    items, total = get_page_audit(page, d)
    html = render_to_string(tmpl, locals())
    response = simplejson.dumps({'success':'success', 'html':html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@app_error_log
@staff_member_required
def get_area_audit(request, tmpl="admin/tags/audit_tag.html"):
    html = ''
    postdata = request.POST.copy()
    year = postdata.get('year', None)
    month = postdata.get('month', None)
    day = postdata.get('day', None)
    area = postdata.get('area', None)
    page = postdata.get('page', None)
    pick_name = '%s.pk' % area
    total_pv = total_uv = sub_pv = sub_uv = 0
    try:
        d = datetime(int(year), int(month), int(day))
    except (TypeError, ValueError):
        html = '<h1>暂无数据</h1>'
    else:
        path, flag = get_and_check_pickfile(d, pick_name, area, page)
        if flag:
            bl = area
            pv_dict = uv_dict = get_normal_pickfile(path)
            total_pv, total_uv = sub_pv, sub_uv = get_sub_pv_uv(pv_dict, uv_dict)
            html = render_to_string(tmpl, locals())
        else:
            pick_file = os.path.join(path, pick_name)
            if os.path.exists(pick_file):
                pv_dict = uv_dict = get_position_pickfile(pick_file, area)
                html = render_to_string(tmpl, locals())
            else:
                for i in xrange(1, settings.LIST_PER_PAGE):
                    bl = area + str(i)
                    pv_dict, uv_dict = get_position_pickfile(path, bl)
                    if area.startswith('s'):
                        sub_pv, sub_uv = get_sub_pv_uv(uv_dict, uv_dict)
                        try:
                            pv_dict.pop('sub_pv')
                            pv_dict.pop('sub_uv')
                        except KeyError:
                            pass
                    else:
                        sub_pv, sub_uv = get_sub_pv_uv(pv_dict, uv_dict)
                    html += render_to_string(tmpl, locals())
                    total_pv += sub_pv
                    total_uv += sub_uv
        if not html.strip():
            html = '<h1>暂无数据</h1>'
        else:
            html = "<h1>%s区总计PV：%s, UV：%s %s" % (area.capitalize(), total_pv, total_uv, html)
    response = simplejson.dumps({'success':'success', 'html':html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@staff_member_required
def show_refer_sort(request, year, month, day, tmpl="admin/audit/show_refer_sort.html"):
    result_list = []
    d = datetime(int(year), int(month), int(day))
    refer_path = os.path.join(settings.LOG_PATH, 'refer')
    mar_name = 'refer_%s_%s_%s.mar' % (d.strftime('%Y'), d.strftime('%m'), d.strftime('%d'))
    refer_file = os.path.join(refer_path, mar_name)
    if os.path.exists(refer_file):
        with open(refer_file, 'r') as f:
            result_list = marshal.load(f)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def add_click_counter(request):
    click_counter()
    success = 'True'
    response = simplejson.dumps({'success':success})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
