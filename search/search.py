import re
import string
from django.db.models import Q
from django.conf import settings
from tuangou.search.models import SearchTerm
from tuangou.stats.utils import stats
from tuangou.utils.location import get_current_city

def store(request, q):
    #if search term is at least three chars long, store  in db
    if len(q) >= 2:
        tracking_id = stats.tracking_id(request)
        terms = SearchTerm.objects.filter(tracking_id=tracking_id, q=q).count()
        if not terms:
            term = SearchTerm()
            term.q = q
            term.tracking_id = stats.tracking_id(request)
            term.ip_address = request.META.get('REMOTE_ADDR')
            term.user = None
            if request.user.is_authenticated():
                term.user = request.user
            term.save()

# get deals matching the search text
def deals(request, search_text):
    from tuangou.guider.models import ReDeal
    city = request.session.get('city', None)
    deals = ReDeal.nonexpires.all()
    results = {}
    results['deals'] = {}
    for word in search_text:
        deals = deals.filter(Q(title__contains=word)|
            Q(division__name__contains=word))
        results['deals'] = deals[:settings.DEAL_PER_ROW]
    return results

