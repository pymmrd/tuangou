from tuangou.commerce.models import CustomCityDeal, MiniCategory
from tuangou.guider.models import ReDeal
from tuangou.utils.location import get_current_city
from tuangou.commerce.utils.cache import cache_jinpin_deals, cache_mini_cats

MINI=4
def jinping_deal(request):
    city = get_current_city(request)
    minis = cache_jinpin_deals(city)
    return minis

def get_mini_category():
    categories = cache_mini_cats()
    return categories
