# -*- coding:utf-8 -*-
from datetime import date
from django.conf import settings
from tuangou.guider.utils.cache import cache_city, cache_domain

def guider_context(request):
    from tuangou.accounts.profile  import retrieve
    keywords = "团购,团购网,团购网站大全,团购导航,团购网站,团购网大全,团购网站导航,团购大全"
    description = "最好的中国团购网站大全,美团,糯米等每日团购网的团购网站导航!汇集北京团购网,上海团购网,和包括广州,深圳,南京,杭州,成都,青岛,西安等的团购网站大全和团购导航"
    nickname = None
    if request.user.is_authenticated():
        profile = retrieve(request)
        nickname = profile.nickname
    return {
        'today': date.today(),
        'domain_name': cache_domain(),
        'nickname': nickname,
        'meta_keywords': keywords,
        'meta_description': description,
        'city': cache_city(settings.DEFAULT_CITY),
        'EXTRA_MEDIA_URL': settings.EXTRA_MEDIA_URL,
    }
