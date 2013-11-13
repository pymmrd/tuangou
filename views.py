# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from tuangou.utils.location import get_current_city, set_current_city

def page_not_found(request, tmpl="404.html"):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    context = u'页面没有找到'
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def server_error(request, tmpl='500.html'):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    context = u'Server Error'
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))
