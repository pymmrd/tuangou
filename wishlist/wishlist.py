#from django
from django.shortcuts import get_object_or_404
#from project
from tuangou.wishlist.models import DealWish
#from pylib
from datetime import date 

def get_wishlist(request):
    from tuangou.wishlist.models import DealWish
    return DealWish.objects.filter(user=request.user)

def add_to_wishlist(request, postdata):
    from tuangou.guider.models import ReDeal
    deal_id = int(postdata.get('wish_deal'))    
    deal = get_object_or_404(ReDeal, pk=deal_id)
    wishlists = get_wishlist(request)
    #check to see if item is already in wishlist
    deal_in_wishlist = False
    for item in wishlists:
        if deal.pk == item.deal.pk:
            item.save()
            deal_in_wishlist = True
    if not deal_in_wishlist:
       dw = DealWish()
       dw.deal = deal
       dw.user = request.user
       dw.save()

def wishlist_distinct_item_count(request):
    return get_wishlist(request).count()

def get_single_item(request, item_id):
    return get_object_or_404(DealWish, id=item_id, user=request.user) 

#remove a single item from 
def remove_from_wishlist(request):
    postdata = request.POST.copy()
    item_id = int(postdata.get('item_id', None))
    wishlist_item = get_single_item(request, item_id)
    if wishlist_item:
        wishlist_item.delete()
