# -*- coding:utf-8 -*-
import re
import time
import uuid
from tuangou.guider.models import City
from tuangou.utils.location import IPInfo, set_current_city
from django.utils.http import cookie_date
from django.http import HttpResponseRedirect
from django.conf import settings

class Location(object):
    def process_request(self, request):
        city_slug = request.COOKIES.get(settings.CITY_COOKIE_NAME, None)
        if city_slug:
            ci = City.objects.get(slug=city_slug)
        else:
            regx = re.compile(u'.+省(?P<name>.+)市')
            ip = request.GET.get('ip', None)
            if ip:
                remote_addr = ip
            else:
                remote_addr = request.META.get('REMOTE_ADDR', None)
            if remote_addr:
                i = IPInfo(settings.QUERY_DB)
                city, address = i.getIPAddr(remote_addr) 
                city = regx.match(city.decode(settings.DEFAULT_CHARSET))
                if city is not None:
                    name = city.group('name')
                    try:
                        ci = City.objects.get(name=name)
                    except City.DoesNotExist:
                        ci = City.objects.get(slug=settings.DEFAULT_CITY)
                else:
                    ci = City.objects.get(slug=settings.DEFAULT_CITY)
                set_current_city(request, ci.slug)

    def process_response(self, request, response):
        max_age = 365 * 24 * 60 * 60
        uuid_cookie_name = 'uuid'
        c_uuid = request.COOKIES.get(uuid_cookie_name, None)
        if c_uuid is None:
            c_uuid = uuid.uuid1()
            response.set_cookie(uuid_cookie_name, c_uuid, max_age)
        return response

        
