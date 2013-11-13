from django.conf.urls.defaults import *

urlpatterns = patterns('wishlist.views',
    (r'^$', 'show_wishlist', {'tmpl':'wishlist/show_wishlist.html'}, 'show_wishlist'),
    (r'^add-wishlist/$', 'add_wishlist'),
    (r'^get-wishlists/$', 'get_wishlists'),
    (r'^delete-wishlists/$', 'delete_wishlists'),
)
