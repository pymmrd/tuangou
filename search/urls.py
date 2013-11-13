from django.conf.urls.defaults import *
from haystack.query import SearchQuerySet
from tuangou.search.forms import CustomSearchForm
from tuangou.search.views import CustomSearchView

sqs = SearchQuerySet()
urlpatterns = patterns('search.views',
    url('^$', 'search', name='haystack_search'),
    #url(r'^$', CustomSearchView(
    #    template ='search/search.html',
    #    searchqueryset = sqs,
    #    form_class = CustomSearchForm,
    #), name='haystack_search'),
)

