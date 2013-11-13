from django import template
from django.conf import settings
from datetime import date
from guider.models import Category, ReDeal, Deal_Shop_City_District, Shop, ViewChart, Website
from guider.utils.guider import _rotate_category_index, _get_category_deals
from guider.utils.cache import cache_category_counter, cache_top_categories, \
                    cache_category, cache_top_districts, cache_category_childs, cache_website
from tuangou.commerce.models import ActivityDeal

register = template.Library()

@register.inclusion_tag("tags/top_categories.html")
def top_categories(slug, cat_slug=None, dist_slug=None, parent=None, page=1):
    result = {}
    categories = cache_top_categories()
    result['categories'] = categories
    result['slug'] = slug
    result['page'] = page
    if cat_slug:
        result['cat_slug'] = cat_slug
    if dist_slug:
        result['dist_slug'] = dist_slug
    if parent:
        result['parent'] = parent
    return result
    
@register.inclusion_tag("tags/district.html")
def district(slug,  cat_slug=None, current_slug=None, page=1):
    result = {}
    districts = cache_top_districts(slug)
    result['page'] = page
    result['districts'] = districts
    result['slug'] = slug
    if cat_slug:
        result['cat_slug'] = cat_slug
    if current_slug:
        result['current_slug'] = current_slug
    return result

@register.inclusion_tag("tags/shop.html")
def deal_shops(deal_id):
    shops= Deal_Shop_City_District.objects.filter(deal_id=deal_id)
    return {'shops': shops}

@register.inclusion_tag('tags/recommend_tag.html')
def recommend_list(deals):
    return {'deals': deals}

@register.inclusion_tag('tags/rotate_category.html')
def rotate_category(city, cat_slug, page_flag):
    index = 0
    page = 1
    MEDIA_URL = settings.MEDIA_URL
    number = settings.LIST_PER_PAGE
    today = date.today()
    try:
        rows, column, area = settings.ROWS_MAP[cat_slug]
    except KeyError:
        rows, column, area = [1, 4, None]
    category = cache_category(cat_slug)
    childs = cache_category_childs(category.slug)
    total = cache_category_counter(city, category)
    deals, paginator = _get_category_deals(city, category, page)
    pageone = number if total > number else total
    offset= _rotate_category_index(rows, column, pageone)
    reserve = pageone - offset
    total_reserve = total - pageone
    result_list = deals[:offset]
    return locals()

@register.tag(name='position')
def position(parser, token):
    tag_name, arg1, arg2 = token.split_contents()
    if not arg1 and not arg2:
        raise template.TemplateSyntaxError, '%r tag requires three argument' % tag_name
    return PositionNode(arg1, arg2)

class PositionNode(template.Node):
    def __init__(self, a, b): 
        self.a = template.Variable(a)
        self.b = template.Variable(b)

    def render(self, context):
        a = self.a.resolve(context)
        b = self.b.resolve(context)
        return (b-1)*settings.LIST_PER_PAGE + a

@register.tag(name='get_deal')
def get_deal(parser, token):
    tag_name, arg = token.split_contents()
    if not arg:
        raise template.TemplateSyntaxError, '%r tag requires one argument' % tag_name
    return DealNode(arg)

class DealNode(template.Node):
    def __init__(self, arg):
        self.arg = template.Variable(arg)

    def render(self, context):
        arg = self.arg.resolve(context)
        context['deal'] = ReDeal.objects.get(pk=arg)
        return ''

@register.tag(name='get_website')
def get_website(parser, token):
    tag_name, arg = token.split_contents()
    if not arg:
        raise template.TemplateSyntaxError, '%r tag requires one argument' % tag_name
    return SiteNode(arg)

class SiteNode(template.Node):
    def __init__(self, arg):
        self.arg = template.Variable(arg)

    def render(self, context):
        arg = self.arg.resolve(context)
        name = cache_website(arg)
        return name
