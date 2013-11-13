from django.conf import settings
from guider.models import City, District
from haystack.forms import SearchForm

def filter_process(queryset, param, city):
    ordering = param.get('ordering', None)
    price = param.get('price', None)
    district = param.get('qdist', None)
    d = None
    if price:
        try:
            price_range = settings.PRICE_RANGE[price]
        except keyError:
            raise Http404
        if isinstance(price_range, tuple):
            queryset = queryset.filter(price__gte=price_range[0], price__lt=price_range[1])
        if isinstance(price_range, int):
            queryset = queryset.filter(price__gte=price_range)
    if district:
        try:
            d = District.objects.active().get(city=city, name=district)
        except District.DoesNotExist:
            return [], d
        else:
            queryset = queryset.filter(district=d.name)
    if ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-obj_pk')
    return queryset, d

class CustomSearchForm(SearchForm):
    def __init__(self, request, *args, **kwargs):
        self.searchqueryset = kwargs.pop('searchqueryset', None)
        self.load_all = kwargs.pop('load_all', False)
        self.data = args[0]
        self.request = request
        if self.searchqueryset is None:
            self.searchqueryset = SearchQuerySet()
        super(self.__class__, self).__init__(*args, **kwargs)

    def search(self):
        dist_slug = None
        city  = self.request.session.get('city', None)
        qdist = self.data.get('qdist', None)
        if not self.is_valid():
            return self.no_query_found(), city, qdist, dist_slug
        if not self.cleaned_data.get('q'):
            return self.no_query_found(), city, qdist, dist_slug
        sqs = self.searchqueryset.auto_query(self.cleaned_data['q']).filter(city=city.name)
        from tuangou.search import search 
        search.store(self.request, self.cleaned_data['q'])
        if self.load_all:
            sqs = sqs.load_all()
        sqs, district = filter_process(sqs, self.data, city)
        dist_slug = district.slug if district else None
        return sqs, city, qdist, dist_slug
