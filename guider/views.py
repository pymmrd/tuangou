# Create your views here.
#-*- coding:utf-8 -*-
#from pylib
from datetime import datetime, date, time

#from django
from django.db.models import Q 
from django.conf import settings
from django.core.cache import cache
from django.utils import simplejson
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse, HttpResponseRedirect
#from project 
from tuangou.guider.models import Website, City, District, Category,\
    DealReview, ReDeal, Website, Deal_Shop_City_District
from tuangou.wishlist.forms import DealWishForm
from tuangou.guider.forms import DealReviewForm 
from tuangou.utils import set_cookie, app_error_log
from tuangou.utils.location import get_current_city, set_current_city
from tuangou.utils.paginator import paginate_util
from tuangou.guider.utils.klass import get_review_partition
from tuangou.guider.templatetags.paginate import smart_page_range
from tuangou.stats.utils.stats import recommended_from_views
from tuangou.commerce.models import ActivityDeal
from tuangou.accounts.profile import retrieve
from tuangou.guider.utils.guider import  _get_district_deals, _get_category_deals,\
        _get_district_category, add_ad_flag, get_feature_deal, get_tags, \
        get_page, get_seo_key
from tuangou.guider.utils.cache import cache_city, cache_district, cache_category,\
        cache_category_counter, cache_friend_links

@app_error_log
def index(request, tmpl="solid/guider/show_city.html"):
    common = 'common'
    page_flag = 'c'
    prefix = 'solid'
    param = request.GET.copy()
    city = get_current_city(request)
    refer = add_ad_flag(request)
    title = "来点团团购导航 - 最大的团购网站大全,团购网首选"
    slug = city.slug
    cname = city.name
    activity = '%s/spec_category.html' % common 
    districts = '%s/%s/district.html' % (prefix, slug) 
    fdeal = '%s/%s/feature_deal.html' % (prefix, slug)
    meishitianxia = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'meishitianxia')
    xiuxianyule = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'xiuxianyule')
    meirongyangsheng = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'meirongyangsheng')
    jiudianlvyou = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'jiudianlvyou')
    huazhuangpin = '%s/%s/%s/%s_rotate_category.html' % (prefix,
                                    slug, 'rotate', 'huazhuangpin')
    fuzhuangshipin = '%s/%s/%s/%s_rotate_category.html' %(prefix, 
                                    slug, 'rotate', 'fuzhuangshipin')
    riyongjiaju = '%s/%s/%s/%s_rotate_category.html' %(prefix,
                                    slug, 'rotate', 'riyongjiaju')
    banner_site, seller_chart, view_chart = get_tags(slug)
    context = RequestContext(request, {'fdeal': fdeal, 
                                        'cname': cname,
                                        'districts':districts, 
                                        'meishitianxia':meishitianxia, 
                                        'meirongyangsheng':meirongyangsheng, 
                                        'fuzhuangshipin':fuzhuangshipin,
                                        'xiuxianyule': xiuxianyule,
                                        'jiudianlvyou':jiudianlvyou, 
                                        'huazhuangpin':huazhuangpin, 
                                        'riyongjiaju':riyongjiaju, 
                                        'slug': slug,
                                        'param': param, 
                                        'title': title, 
                                        'banner_site':banner_site, 
                                        'seller_chart':seller_chart, 
                                        'view_chart':view_chart,
                                        'page_flag':page_flag,
                                        })
    return render_to_response(tmpl, context)
"""

@app_error_log
def index(request, tmpl='guider/show_city.html'):
    page_flag = 'c' 
    param = request.GET.copy()
    refer = add_ad_flag(request)
    city = get_current_city(request)
    fdeal = get_feature_deal(city) 
    cname, slug = city.name, city.slug
    title = "来点团团购导航 - 最大的团购网站大全,团购网首选"
    banner_site, seller_chart, view_chart = get_tags(slug)
    context = RequestContext(request, {'fdeal': fdeal,
                                        'cname': cname,
                                        'slug': slug,
                                        'title': title,
                                        'param': param,
                                        'banner_site':banner_site, 
                                        'seller_chart':seller_chart, 
                                        'view_chart':view_chart,
                                        'page_flag':page_flag,
                                        })
    return render_to_response(tmpl, context)
"""

@app_error_log
@set_cookie
def show_city(request, slug, tmpl='guider/show_city.html'):
    common = 'common'
    page_flag = 'c'
    prefix = 'solid'
    param = request.GET.copy()
    city = cache_city(slug)
    set_current_city(request, slug)
    refer = add_ad_flag(request)
    slug = city.slug
    cname = city.name
    banner_site, seller_chart, view_chart = get_tags(slug)
    t = "%s团购网,%s团购网站大全,团购网 %s,%s团购大全,%s团购导航在来点团"
    title = t % (cname, cname, cname, cname, cname)
    districts = '%s/%s/district.html' % (prefix, slug) 
    fdeal = '%s/%s/feature_deal.html' % (prefix, slug)
    meishitianxia = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'meishitianxia')
    xiuxianyule = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'xiuxianyule')
    meirongyangsheng = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'meirongyangsheng')
    jiudianlvyou = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'jiudianlvyou')
    huazhuangpin = '%s/%s/%s/%s_rotate_category.html' % (prefix, 
                                    slug, 'rotate', 'huazhuangpin')
    fuzhuangshipin = '%s/%s/%s/%s_rotate_category.html' %(prefix, 
                                    slug, 'rotate', 'fuzhuangshipin')
    riyongjiaju = '%s/%s/%s/%s_rotate_category.html' %(prefix, 
                                    slug, 'rotate', 'riyongjiaju')
    context = RequestContext(request, {
                                    'fdeal': fdeal, 
                                    'districts':districts, 
                                    'xiuxianyule': xiuxianyule,
                                    'meishitianxia':meishitianxia, 
                                    'meirongyangsheng':meirongyangsheng, 
                                    'jiudianlvyou':jiudianlvyou, 
                                    'fuzhuangshipin':fuzhuangshipin,
                                    'huazhuangpin':huazhuangpin, 
                                    'riyongjiaju':riyongjiaju, 
                                    'param': param, 
                                    'title': title, 
                                    'slug': slug,
                                    'banner_site':banner_site, 
                                    'seller_chart':seller_chart, 
                                    'view_chart':view_chart,
                                    'cname': cname,
                                    'page_flag':page_flag,
                                })
    return render_to_response(tmpl, context)

@app_error_log
@set_cookie
def show_district(request, slug, dist_slug, page, tmpl='guider/show_district.html'):
    page_flag = 'd'
    t = u'%s团购网,%s%s团购大全,%s团购网站大全 - 来点团%s团购'
    k = u'%s团购网,%s%s团购大全,%s团购'
    d = u'%s团购，尽在【来点团团购导航】。汇集美团网%s，大众点评%s，满座，糯米，58团购等数百个团购网优惠信息，是%s首选的团购大全网站。'
    page = get_page(page)
    param = request.GET.copy()
    refer = add_ad_flag(request)
    city = cache_city(slug)
    set_current_city(request, slug)
    district = cache_district(city, dist_slug)
    dname = district.name
    cname = city.name
    title = t % (dname, cname, dname, cname, cname)
    meta_keywords = k % (dname, cname, dname, dname)
    meta_description = d % (dname, cname, cname, cname)
    banner_site, seller_chart, view_chart = get_tags(slug)
    result_list, paginator = _get_district_deals(city, district, page, param)
    context = RequestContext(request,{
                                    'param':param, 
                                    'page':page, 
                                    'slug':slug, 
                                    'cname': cname,
                                    'dist_slug':dist_slug, 
                                    'title':title, 
                                    'meta_keywords': meta_keywords,
                                    'meta_description':meta_description,
                                    'banner_site':banner_site,
                                    'seller_chart':seller_chart,
                                    'view_chart': view_chart,
                                    'page_flag': page_flag,
                                    'result_list':result_list,
                                    'paginator':paginator,
                            })
    return render_to_response(tmpl, context)

@app_error_log
@set_cookie
def show_category(request, slug, cat_slug, page, tmpl='guider/show_category.html'):
    page_flag = 'ca'
    page = get_page(page)
    param = request.GET.copy()
    refer = add_ad_flag(request)
    city = cache_city(slug)
    set_current_city(request, slug)
    cname = city.name
    category = cache_category(cat_slug)
    seo_key = get_seo_key(category)
    ctitle = category.title
    title = u'%s%s团购网,%s%s团购大全,%s团购网站大全 - 来点团%s团购' % (cname,
                                            ctitle, cname, seo_key, cname, cname)
    meta_keywords = category.meta_keywords.replace('%s', cname)
    meta_description = category.meta_description.replace('%s', cname)
    parents = category.parents()
    parent =  parents[0] if parents else category
    result_list, paginator = _get_category_deals(city, category, page, param)
    context = RequestContext(request,{
                                    'page_flag':page_flag,
                                    'param': param,
                                    'refer': refer,
                                    'title': title,
                                    'slug': slug,
                                    'cname': cname,
                                    'page': page,
                                    'cat_slug': cat_slug,
                                    'parent': parent,
                                    'result_list': result_list,
                                    'paginator': paginator,
                                    'meta_keywords':meta_keywords,
                                    'meta_description': meta_description,
                                })
    return render_to_response(tmpl, context)

@app_error_log
@set_cookie
def show_district_category(request, slug, dist_slug, cat_slug, page, tmpl='guider/show_district_category.html'):
    t = u'%s%s团购网,%s%s%s团购大全,%s团购网站大全 - 来点团%s团购'
    k = u'%s%s团购网,%s%s%s团购大全,%s%s团购'
    d = u'%s%s团购，尽在【来点团团购导航】。汇集美团网%s，大众点评%s，满座，糯米，58团购等数百个团购网优惠信息，是%s%s团购首选的团购大全网站。'
    page_flag = 'da'
    page = get_page(page)
    param = request.GET.copy()
    city = cache_city(slug)
    set_current_city(request, slug)
    refer = add_ad_flag(request)
    category = cache_category(cat_slug)
    parents = category.parents()
    district = cache_district(city, dist_slug)
    cname = city.name
    dname = district.name
    seo_key = get_seo_key(category)
    ctitle = category.title
    title = t % (dname, ctitle, cname, dname, seo_key, cname, cname) 
    meta_keywords = k % (dname, ctitle, cname, dname, seo_key, dname, seo_key)
    meta_description = d %(dname, ctitle, cname, cname, cname, seo_key)
    parent =  parents[0] if parents else category
    result_list, paginator = _get_district_category(city, district, category, page, param)
    context = RequestContext(request,{
                                    'page_flag':page_flag,
                                    'param': param,
                                    'refer': refer,
                                    'title': title,
                                    'slug': slug,
                                    'cname': cname,
                                    'page': page,
                                    'dist_slug': dist_slug,
                                    'cat_slug': cat_slug,
                                    'parent': parent,
                                    'meta_keywords': meta_keywords,
                                    'meta_description': meta_description,
                                    'result_list': result_list,
                                    'paginator': paginator,
                            })
    return render_to_response(tmpl, context)

@app_error_log
def show_deal_detail(request, deal_id, tmpl="guider/show_deal.html"): 
    shop = None
    profile = None
    k = u'%s团购网,%s团购大全,%s团购'
    d = u'%s团购，尽在【来点团团购导航】。汇集美团网%s，大众点评%s，满座，糯米，58团购等数百个团购网优惠信息，是%s首选的团购大全网站。'
    param = request.GET.copy()
    area = param.get('area', None)
    r = param.get('r', None)
    if request.user.is_authenticated():
        profile = retrieve(request)
    city = get_current_city(request)
    cname = city.name
    slug = city.slug
    deal_id = int(deal_id)
    deal = get_object_or_404(ReDeal, pk=int(deal_id))
    category = deal.category
    shops = Deal_Shop_City_District.objects.filter(deal_id=deal_id)
    if shops:
        shop = shops[0].shop.name
        meta_keywords = '%s%s－' % (cname, shop) + k % (cname, cname, cname)
        meta_description = '%s%s－' %(cname, shop) + d % (cname, cname, cname, cname)
    else:
        meta_keywords = k % (cname, cname, cname)
        meta_description = d % (cname, cname, cname, cname)
    from tuangou.stats.utils import stats
    stats.log_deal_view(request, deal)
    wishform = DealWishForm() 
    wishform.fields['wish_deal'].widget.attrs['value'] = deal.id
    #similar_views = recommended_from_views(request)
    similar_views = []
    if similar_views:
        similar_views = similar_views[:settings.DEAL_PER_ROW]
    reviewform = DealReviewForm()
    reviewform.fields['deal_id'].widget.attrs['value'] = deal.id
    model = get_review_partition(deal.id)
    reviews = model.objects.filter(deal=deal)
    review_counter = reviews.count()
    banner_site, seller_chart, view_chart = get_tags(city.slug)
    result_list, paginator, page = paginate_util(reviews, param ,settings.PER_PAGE_COMMENTS) 
    context = RequestContext(request,{
                                     'area': area,
                                     'shop': shop,
                                     'r': r, 
                                     'profile': profile,
                                     'cname': cname,
                                     'slug': slug,
                                     'deal': deal,
                                     'category': category,
                                     'shops':shops,
                                     'meta_description': meta_description,
                                     'meta_keywords': meta_keywords,
                                     'wishform': wishform,
                                     'similar_views': similar_views,
                                     'reviewform': reviewform,
                                     'review_counter': review_counter,
                                     'result_list': result_list,
                                     'paginator': paginator,
                                     'banner_site': banner_site,
                                     'seller_chart': seller_chart,
                                     'view_chart': view_chart,
                                })
    return render_to_response(tmpl, context)

@csrf_exempt
@app_error_log
@login_required
def get_reviews(request, tmpl="tags/review_list.html"):
    flag = 'True'
    param = request.GET.copy()
    try:
        deal_id = int(param.get('deal_id', None))
    except (ValueError, TypeError):
        raise Http404
    deal = get_object_or_404(ReDeal, pk=deal_id)
    model = get_review_partition(deal.id)
    reviews = model.objects.filter(deal=deal)
    result_list, paginator, page = paginate_util(reviews, param , settings.PER_PAGE_COMMENTS) 
    html = render_to_string(tmpl, locals())
    page_range = smart_page_range(paginator.num_pages, page)
    p = paginator.page(page)
    page_html = render_to_string('tags/more_paginator.html', locals())
    response = simplejson.dumps({'html':html, 'success':'True', 'page_html': page_html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@app_error_log
@login_required
def add_deal_review(request, tmpl="tags/review_tags.html"):
    if request.user.is_active:
        postdata = request.POST.copy()
        form = DealReviewForm(postdata)
        if form.is_valid():
            deal_id = form.cleaned_data['deal_id']
            comment  = form.cleaned_data['comment']
            deal = get_object_or_404(ReDeal, pk=deal_id)
            model = get_review_partition(deal_id)
            now = datetime.now()
            new  = model(comment=comment, 
                        deal=deal,
                        user=request.user, 
                        ip_address=request.META.get('REMOTE_ADDR', None), 
                        submit_date=now
                        )
            profile = request.user.get_profile()
            item = form.check_for_duplicate_comment(model, new)
            item.submit_date= now
            item.save()
            html = render_to_string(tmpl, locals())
            response = simplejson.dumps({'success':'True', 'html':html})
        else:
            response = simplejson.dumps({'success':'False'})
    else:
        msg = '请到您的邮箱%s 激活帐号, 谢谢！' % ( request.user.username)
        response = simplejson.dumps({'success': 'False', 'msg': msg})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
def sites(request, tmpl="guider/sites.html"):
    tag = "tags/%s_sites.html" 
    param = request.GET.copy()
    flag = param.get('flag', None)
    if flag:
        slug = param.get('slug', None)
        name = param.get('name', None)
        tag = "tags/sites/%s_sites.html" % slug 
        html = render_to_string(tag, locals())
        response = simplejson.dumps({'success':'True', 'html':html})
        return HttpResponse(response, content_type='application/javascript; charset=utf-8')
    else:
        city = get_current_city(request)
        slug = city.slug
        tag = "tags/sites/%s_sites.html" % slug 
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@app_error_log
def open_api(request, tmpl="guider/open_api.html"):
    city = get_current_city(request)
    cname = city.name
    slug = city.slug
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@app_error_log
def search_city_form(request):
    name = request.POST.get('name')
    name = name.strip()
    try:
        city = City.objects.get(Q(name=name)|Q(slug=name))
    except City.DoesNotExist:
        success = 'False'
        msg = u'没有找到您要查找城市' 
    else:
        success = 'True'
        msg = city.slug
    response = simplejson.dumps({'success':success, 'msg':msg})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
def get_reserve_deals(request, tmpl="tags/deal_list.html"):
    page = 1
    page_flag = 'c'
    number = settings.LIST_PER_PAGE
    MEDIA_URL = settings.MEDIA_URL
    params = request.GET.copy()
    index = int(params.get('index'))
    title = params.get('title')
    category = get_object_or_404(Category, title=title)
    try:
        rows, num, area = settings.ROWS_MAP[category.slug]
    except KeyError:
        rows, num, area = [1, 4, None]
    city = get_current_city(request)
    deals, num_pages = _get_category_deals(city, category, page)
    dn = cache_category_counter(city, category)
    offset =  number if dn > number else dn 
    reserve = dn - number
    se = slice(index, offset)
    result_list = deals[se]
    html = render_to_string(tmpl, locals())
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
def show_friend_links(request, tmpl):
    city = get_current_city(request)
    cname = city.name
    slug = city.slug
    object_list = cache_friend_links()
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def download(request, tmpl):
    city = get_current_city(request)
    cname = city.name
    slug = city.slug
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))
    

