# Create your views here.
#from django
from django.conf import settings
from django.utils import simplejson
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required 
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
#from project
from tuangou.utils import app_error_log
from tuangou.utils.location import get_current_city
from tuangou.wishlist.forms import DealWishForm
from tuangou.accounts.profile import retrieve
from tuangou.utils.paginator import paginate_util
from tuangou.wishlist.feed import WishListFeed
from tuangou.wishlist.wishlist import add_to_wishlist, \
                wishlist_distinct_item_count, get_wishlist, remove_from_wishlist
from tuangou.guider.templatetags.paginate import smart_page_range
#from pylib
from datetime import datetime

@csrf_exempt
@app_error_log
@login_required
def add_wishlist(request):
    counter = wishlist_distinct_item_count(request)
    if counter < settings.WISHLIST_LIMIT:
        postdata = request.POST.copy()
        form = DealWishForm(postdata) 
        if form.is_valid():
            add_to_wishlist(request, postdata)
            success = 'True'
            message = WishListFeed.ADD_SUCCESS
        else:
            success = 'False'
            message = WishListFeed.PARAM_ERROR
    else:
        success = 'False'
        message = WishListFeed.ACHIEVE_LIMIT
    response = simplejson.dumps({'success': success, 'message': message})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
@login_required
def show_wishlist(request, tmpl='wishlist/show_wishlist.html'):
    now = datetime.now()
    param = request.GET.copy()
    profile = retrieve(request)    
    city = get_current_city(request)
    wishlists = get_wishlist(request)
    wish_counter = wishlists.count()
    result_list, paginator, page = paginate_util(wishlists, param ,settings.WISH_PER_PAGE) 
    p = paginator.page(page)
    context = RequestContext(request, {
                                        'slug': city.slug,
                                        'cname': city.name,
                                        'wish_counter':wish_counter,
                                        'result_list': result_list,
                                        'paginator': paginator, 
                                        'page': page,
                                        'p':p,
                                        'profile': profile,
                                        'param': param,
                                        'now': now,
                            })
    return render_to_response(tmpl, context)

@csrf_exempt
@app_error_log
@login_required
def get_wishlists(request, tmpl="tags/wishlist.html"):
    param = request.GET.copy()
    wishlists = get_wishlist(request)
    result_list, paginator, page = paginate_util(wishlists, param , settings.WISH_PER_PAGE) 
    html = render_to_string(tmpl, locals())
    page_range = smart_page_range(paginator.num_pages, page)
    flag = 'True'
    p = paginator.page(page)
    page_html = render_to_string('tags/more_paginator.html', locals())
    response = simplejson.dumps({'html':html, 'success':'True', 'page_html': page_html})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@app_error_log
@login_required
def delete_wishlists(request):
    try:
        remove_from_wishlist(request)
    except: 
        success = 'False'
    else:
        success = 'True'
    response = simplejson.dumps({'success':success})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

