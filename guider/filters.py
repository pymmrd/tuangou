from django.http import Http404
from django.conf import settings

def filter_process(queryset, *param):
    ordering, price = param
    if price:
        try:
            price_range = settings.PRICE_RANGE[price]
        except keyError:
            raise Http404
        if isinstance(price_range, tuple):
            queryset = queryset.filter(price__range=price_range)
        if isinstance(price_range, int):
            queryset = queryset.filter(price__gte=price_range)
    if ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-pk')
    return queryset
