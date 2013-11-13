import os
import base64
from django.conf import settings
from tuangou.stats.models import DealView
from tuangou.utils.location import get_current_city
from tuangou.guider.models import ReDeal

def tracking_id(request):
    try:
        return request.session['tracking_id']
    except KeyError:
        request.session['tracking_id'] = base64.b64encode(os.urandom(36))
        return request.session['tracking_id']

def recommended_from_search(request):
    from tuangou.search import search
    # get the common words from the stored searches
    common_words = frequent_search_words(request)
    matching = []
    for word in common_words:
        results = search.deals(request, word).get('deals',[])
        for r in results:
            if len(matching) < settings.DEAL_PER_ROW and not r in matching:
                matching.append(r)
    return matching

def frequent_search_words(request): 
    from search.models import SearchTerm
    # get the ten most recent searches from the database.
    searches = SearchTerm.objects.filter(tracking_id=tracking_id(request)).values('q').order_by('-search_date')[0:10]
    # join all of the searches together into a single string.
    search_string = ' '.join([search['q'] for search in searches])
    # return the top three most common words in the searches
    return sort_words_by_frequency(search_string)[0:3]

def sort_words_by_frequency(some_string):
    # convert the string to a python list
    words = some_string.split()
    # assign a rank to each word based on frequency
    ranked_words = [[word, words.count(word)] for word in set(words)]
    # sort the words based on descending frequency
    sorted_words = sorted(ranked_words, key = lambda word: -word[1])
    # return the list of words, most frequent first
    return [p[0] for p in sorted_words]

def log_deal_view(request, deal):
    t_id = tracking_id(request)
    city = get_current_city(request)
    try:
        v = DealView.objects.get(tracking_id=t_id, deal=deal, city=city)
        v.save()
    except DealView.DoesNotExist:
        v = DealView()
        v.deal = deal
        v.ip_address = request.META.get('REMOTE_ADDR')
        v.tracking_id = t_id
        v.city = city
        v.user = None
        if request.user.is_authenticated():
            v.user = request.user
        v.save()

def recommended_from_views(request):
    city = get_current_city(request)
    t_id = tracking_id(request)
    #get recently viewed deals
    viewed = get_recently_viewed(request)
    #if there are previously viewed products, get_other tracking ids that have
    #viewed those products also
    if viewed:
        dealviews = DealView.objects.filter(deal__in=viewed).values('tracking_id')
        t_ids = [v['tracking_id'] for v in dealviews]
        #if there are other tracking ids, get other products
        if t_ids:
            all_viewed = ReDeal.nonexpires.filter(dealview__tracking_id__in=t_ids)
            #if there are other deals, get them , excluding the 
            #deals that the customer has already viewed
            if all_viewed:
                other_viewed = DealView.objects.filter(deal__in=all_viewed).exclude(deal__in=viewed)
                if other_viewed:
                    return ReDeal.nonexpires.filter(dealview__in=other_viewed).filter(division=city).distinct()

def get_recently_viewed(request):
    t_id = tracking_id(request)
    views = DealView.objects.filter(tracking_id=t_id).values('deal_id').order_by('-date')[0: settings.DEAL_PER_ROW]
    deal_ids = [v['deal_id'] for v in views]
    return ReDeal.nonexpires.filter(id__in=deal_ids)
