from django import template
from django.conf import settings
from tuangou.commerce.models import ActivityDeal, CarouselAd
from tuangou.commerce.utils.cache import cache_mini_items, cache_channel_img, \
    cache_mini_category, cache_mini_category_deal

register = template.Library()
@register.inclusion_tag("tags/carousel.html")
def show_carousels(refer, page_flag):
    carousels = CarouselAd.objects.all()
    return locals()

@register.tag(name='get_position')
def get_position(parser, token):
    tag_name, arg = token.split_contents()
    if not arg:
        raise template.TemplateSyntaxError, '%r tag requires one argument' % tag_name
    return ActivityNode(arg)

class ActivityNode(template.Node):
    def __init__(self, arg):
        self.arg = template.Variable(arg)

    def render(self, context):
        arg = self.arg.resolve(context)
        try:
            ad = ActivityDeal.objects.values('position').get(deal_id=arg)
            position = ad['position']
        except ActivityDeal.DoesNotExist:
            position = ''
        return position

@register.inclusion_tag('tags/miniitem.html')
def retrieve_items(slug):
    miniitems = cache_mini_items(slug)
    return locals()

@register.inclusion_tag('tags/mini_carousel.html')
def retrieve_img(slug, flag=None):
    MEDIA_URL = settings.MEDIA_URL
    img = cache_channel_img(slug)
    return locals()

@register.inclusion_tag("tags/jinpin_deal.html")
def mini_category_deal(request, city, slug):
    MEDIA_URL = settings.MEDIA_URL
    category = cache_mini_category(slug)
    deals = cache_mini_category_deal(city, category)
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
        return (b-1)*settings.APP_LIST_PER_PAGE + a
