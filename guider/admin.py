# -*- coding:utf-8 -*-
from django.contrib import admin
from guider.models import *

def get_object_id(request):
    path_info = request.META.get('PATH_INFO', None)
    object_id = path_info.rsplit('/', 2)[-2]
    return object_id

class DealAdmin(admin.ModelAdmin):
    list_display = ('prepare_title','category','prepare_city', 
            'prepare_district', 'price', 'discount', 'bought', 
            'start_date', 'end_date', 'website', 'check_deal', 'is_active')
    search_fields = ('id', 'title','category__title' )
    list_per_page = 200
    filter_horizontal= ('division', )
    list_select_related = True

    def prepare_title(self, obj):
        return obj.title[:50]
    prepare_title.short_description = '标题'

    def check_deal(self, obj):
        return "<a href='%s' target='_blank'>%s</a>" % (obj.deal_url, u'点击查看')
    check_deal.allow_tags = True
    check_deal.short_description = '活动地址'

    def prepare_city(self, obj):
        return ', '.join([city.name for city in obj.division.all()])
    prepare_city.short_description = '城市'

    def prepare_district(self, obj):
        return ', '.join([district.name for district in obj.district.all()])
    prepare_district.short_description = '商区'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'division':
            kwargs['queryset'] = City.actives.order_by('slug')
        if db_field.name == 'district':
            kwargs['queryset'] = District.objects.active().order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class DealFieldMapInline(admin.TabularInline):
    model = DealFieldMap
    extra = 0

class CityAPINameInline(admin.TabularInline):
    model = CityAPIName
    extra = 0

class WebsiteAdmin(admin.ModelAdmin):
    list_display =('__unicode__', 'site_url', 'activity_url', 'city_api', 'deal_crawl_type', 'city_crawl_type', 'date_fmt', 'is_active', 'is_famous', 'weight')
    search_fields = ('name', 'url',)
    list_filter =  ('is_active',)
    filter_horizontal = ('opened_city',)
    list_select_related = True
    inlines = [DealFieldMapInline]

    def site_url(self, obj):
        return "<a href='%s' target='_blank'>%s</a>" % (obj.url, obj.url)
    site_url.allow_tags = True
    site_url.short_description = u'地址'
    
    def activity_url(self, obj):
        return "<a href='%s' target='_blank'>%s</a>" %(obj.deal_api, obj.deal_api)
    activity_url.allow_tags = True
    activity_url.short_description = u'活动API'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'opened_city':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'city', 'is_active')
    search_fields =('name', 'slug', 'city__name')
    list_filter =  ('is_active', )
    list_select_related = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            kwargs['queryset'] = City.actives.order_by('slug')
        if request.path.endswith('/add/'):
            if db_field.name == 'parent':
                kwargs['queryset'] = District.objects.active().filter(parent=None)
        else:
            object_id = get_object_id(request)
            obj = District.objects.get(pk=object_id)
            if db_field.name == 'parent':
                kwargs['queryset'] = District.objects.active().filter(parent=None, city=obj.city)
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_date', 'is_active')
    list_filter =  ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ['slug',]
    list_per_page = 200
    #inlines = [DistrictInline]

class MatchWordAdmin(admin.TabularInline):
    model = MatchWord
    extra = 0

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('path','slug', 'level')
    list_display_links = ('path', 'slug')
    inlines = [MatchWordAdmin, ]

class ViewChartAdmin(admin.ModelAdmin):
    list_display = ('deal','rank', 'city')
    raw_id_fields = ('deal', )
    list_filgter = ('is_active', 'city')
    list_display_links =('deal', )
    ordering = ['-rank']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class SellerChartAdmin(admin.ModelAdmin):
    list_display = ('deal', 'quantity', 'city')
    list_display_links = ('deal',)
    raw_id_fields = ('deal', )
    list_filter = ('is_active', 'city')
    ordering = ['-quantity']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ShopAdmin(admin.ModelAdmin):
    list_display  = ('name', 'telephone', 'url', 'longitude', 'latitude',  'address')
    list_dispaly_links = ('name', 'url', 'telephone')
    ordering = ['name']
    search_fields = ('id', )
    list_per_page = 200

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class DealShopCityDistrictAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'shop', 'get_shop_lng', 
        'get_shop_lat',  'city', 'district', 
        'parent_district', 'get_website', 'check_deal' )
    search_fields = ('deal_id', )

    def queryset(self, request):
        ids = ReDeal.nonexpires.values_list('pk', flat=True)
        qs = super(self.__class__, self).queryset(request)
        queryset = qs.filter(deal_id__in=ids).order_by('-pk')
        return queryset

    def parent_district(self, obj):
        return obj.district.parent
    parent_district.short_description = u'父商区'

    def check_deal(self, obj):
        deal = ReDeal.nonexpires.values('deal_url').get(pk=obj.deal_id)
        return "<a href='%s' target='_blank'>%s</a>" % (deal['deal_url'], u'点击查看')
    check_deal.allow_tags = True
    check_deal.short_description = '活动地址'

    def get_website(self, obj):
        deal = ReDeal.nonexpires.values('website__name').get(pk=obj.deal_id)
        return deal['website__name']
    get_website.short_description = '活动地址'

    def get_shop_lng(self, obj):
        return obj.shop.longitude
    get_shop_lng.short_description = u'经度'

    def get_shop_lat(self, obj):
        return obj.shop.latitude
    get_shop_lat.short_description = u'纬度'

class DealReviewAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'comment', 'submit_date', 'is_remove', 'ip_address')


admin.site.register(FriendLink)
admin.site.register(Shop, ShopAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(ReDeal, DealAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(ViewChart, ViewChartAdmin)
admin.site.register(SellerChart, SellerChartAdmin)
admin.site.register(Deal_Shop_City_District, DealShopCityDistrictAdmin)
admin.site.register(DealReview0, DealReviewAdmin)
admin.site.register(DealReview1, DealReviewAdmin)
admin.site.register(DealReview2, DealReviewAdmin)
admin.site.register(DealReview3, DealReviewAdmin)
admin.site.register(DealReview4, DealReviewAdmin)
admin.site.register(DealReview5, DealReviewAdmin)
admin.site.register(DealReview6, DealReviewAdmin)
admin.site.register(DealReview7, DealReviewAdmin)
admin.site.register(DealReview8, DealReviewAdmin)
admin.site.register(DealReview9, DealReviewAdmin)
