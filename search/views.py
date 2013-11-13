# -*- coding:utf-8 -*-
# Create your views here.
from haystack.views import SearchView
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response
from tuangou.guider.utils.guider import get_tags
from tuangou.guider.models import ReDeal
from tuangou.utils.paginator import paginate_util
from tuangou.utils import set_cookie, app_error_log
from tuangou.utils.location import get_current_city
from tuangou.guider.filters import filter_process

class CustomSearchView(SearchView):
    def build_form(self, form_kwargs=None):
        """
        Instantiates the form the class should use to process the search query.
        """
        data = None
        kwargs = {
            'load_all': self.load_all,
        }

        if form_kwargs:
            kwargs.update(form_kwargs)
        
        if len(self.request.GET):
            data = self.request.GET
        
        if self.searchqueryset is not None:
            kwargs['searchqueryset'] = self.searchqueryset
        return self.form_class(self.request, data, **kwargs)
    
    def __call__(self, request):
        """
        Generates the actual response to the search.
        
        Relies on internal, overridable methods to construct the response.
        """
        self.request = request
        self.form = self.build_form()
        self.query = self.get_query()
        self.results, city, qdist, dist_slug = self.get_results()
        return self.create_response(city, qdist, dist_slug)

    def create_response(self, city, qdist, dist_slug):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()
        banner_site, seller_chart, view_chart = get_tags(city.slug)
        context = {
            'city':city,
            'page': page,
            'qdist': qdist,
            'slug':city.slug,
            'form': self.form,
            'suggestion': None,
            'query': self.query,
            'param': self.request.GET.copy(),
            'dist_slug': dist_slug, 
            'paginator': paginator,
            'banner_site': banner_site,
            'seller_chart': seller_chart,
            'view_chart': view_chart,
        }
        
        if getattr(settings, 'HAYSTACK_INCLUDE_SPELLING', False):
            context['suggestion'] = self.form.get_suggestion()
        
        context.update(self.extra_context())
        return render_to_response(self.template, context, context_instance=self.context_class(self.request))

VALUES = ('pk', 'title', 'end_date','image', 'start_date', 'deal_url', 'price', 'origin_price', 'discount', 'bought', 'is_ad', 'website__name')
@app_error_log
def search(request, tmpl='search/search_result.html'):
    t = "%s%s团购网,%s%s优惠券,%s%s打折信息 - 来点团%s团购导航"
    k = "团购%s,%s团购,%s%s团购,%s%s团购网"
    d = "%s%s团购，尽在【来点团团购导航】。%s%s团购，%s%s优惠券，%s%s打折等优惠信息。来点团为您汇集%s%s团购网活动及团购点评，上百家团购网站信息供您选择。"
    object_list = []
    param = request.GET.copy()
    query = param.get('q', None)
    qdist = param.get('qdist', None)
    ordering = param.get('ordering', None)
    price = param.get('price', None)
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    title = t % (cname, query, cname, query, cname, query, cname)
    meta_keywords = k % (query, query, cname, query, cname, query)
    meta_description = d % (cname, query, cname, query, cname, query, cname, query, cname, query) 
    if query:
        from tuangou.search import search 
        search.store(request, query)
        queryset = ReDeal.nonexpires.filter(Q(division=city), Q(title__icontains=query)|Q(website__name__icontains=query))
        if qdist:
            queryset = queryset.filter(district__name=qdist)
        queryset = queryset.values(*VALUES)
        object_list = filter_process(queryset, ordering, price)
    else:
        query = ''
    banner_site, seller_chart, view_chart = get_tags(slug)
    result_list, paginator, page = paginate_util(object_list, param, settings.LIST_PER_PAGE)
    context = RequestContext(request, {
                                'param': param,
                                'query': query,
                                'qdist': qdist,
                                'slug': slug,
                                'city': city,
                                'cname':cname,
                                'title': title,
                                'meta_keywords': meta_keywords,
                                'meta_description': meta_description,
                                'query': query,
                                'view_chart': view_chart,
                                'banner_site': banner_site,
                                'seller_chart': seller_chart,
                                'result_list': result_list,
                                'paginator': paginator,
                                'page': page,
                                'qdist': qdist,
                                'price': price,
                                'ordering': ordering,
                            })
    return render_to_response(tmpl, context)
