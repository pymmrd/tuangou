from django import template
from tuangou.utils.cache import get_category_cache, get_districts_cache
from guider.models import Category, ReDeal, Deal_Shop_City_District, Shop, ViewChart
from tuangou.guider.utils.cache import cache_top_districts

register = template.Library()
@register.inclusion_tag("tags/search_district_tag.html")
def search_district(request, city, current_slug=None):
    param = request.GET.copy()
    districts = cache_top_districts(city)
    return locals()
