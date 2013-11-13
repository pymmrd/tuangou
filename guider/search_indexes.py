from haystack.indexes import *
from haystack import site
from tuangou.guider.models import ReDeal
from datetime import date
from pymmseg import mmseg

mmseg.dict_load_defaults()

def tokens(text):
    algor = mmseg.Algorithm(text)
    terms = " ".join([tok.text for tok in algor])
    return terms

class DealIndex(SearchIndex):
    text = CharField(document=True)
    obj_pk = IntegerField(model_attr='pk')
    title = CharField(model_attr='title')
    website = CharField(model_attr='website')
    city = MultiValueField()
    district = MultiValueField()
    start_date = DateTimeField(model_attr='start_date')
    bought = IntegerField(model_attr='bought')
    price = FloatField(model_attr='price')
    discount = FloatField(model_attr='discount')
    rendered = CharField(use_template=True, indexed=False, template_name='tags/deal_rendered.txt')

    def get_model(self):
        return ReDeal

    def index_queryset(self):
        #return self.get_model().objects.filter(start_date__gte=date.today())
        return self.get_model().nonexpires.all()

    def prepare_website(self, obj):
        return obj.website.name.encode('utf-8')

    def prepare_city(self, obj):
        cities = [city.name.encode('utf-8') for city in obj.division.filter(is_active=True)]
        return cities

    def prepare_district(self, obj):
        districts =  [district.parent.name.encode('utf-8') for district in obj.district.all() if district.parent]
        return districts

    def prepare_title(self, obj):
        return tokens(obj.title.encode('utf-8'))

site.register(ReDeal, DealIndex)
