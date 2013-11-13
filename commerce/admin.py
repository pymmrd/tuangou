# -*- coding:utf-8 -*-
from django.contrib import admin
from tuangou.guider.models import City, District, Category, ReDeal, Website
from tuangou.commerce.models import *

class AdvertisementAdmin(admin.ModelAdmin):
    list_display=('id', 'start_time', 'expire_time', 'show_times', 'show_times_per_day',  'width', 'height', 'is_active')
    list_filter = ('is_active', )
    list_dipslay_links = ('id', 'title')
    search_fields=('title', 'id')
    filter_horizontal= ('dispatch_city', )

class CityConstrainAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'start_time', 'expire_time', 'show_times', 'show_times_per_day', 'is_active')
    list_filter = ('is_active', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'division':
           kwargs['queryset'] = City.actives.filter(is_active=True).order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

def website(obj):
    deal = ReDeal.objects.get(pk=obj.deal_id)
    return deal.website.name
website.short_description = u'站点'

def prepare_title(obj):
    deal = ReDeal.objects.get(pk=obj.deal_id)
    return deal.title[:50]
prepare_title.short_description = '标题'

class CustomCityDealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'division', prepare_title, website, 'position', 'is_active') 
    ordering = ['position']
    list_select_related = True 
    list_filter = ('is_active', 'attribute')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'division':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class CustomCategoryDealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'division', prepare_title, website, 'category', 'position','is_active')
    ordering = ['position']
    list_select_related = True 
    list_filter = ('is_active', )
    search_fields = ('deal_id', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'division':
            kwargs['queryset'] = City.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class CustomDistrictDealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'division', 'district', prepare_title, website, 'position', 'is_active')
    ordering = ['position']
    list_select_related = True 
    list_filter = ('is_active', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'division':
            kwargs['queryset'] = City.actives.order_by('slug')
        if db_field.name == 'district':
            kwargs['queryset'] = District.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class CustomCategoryByDistrictAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'division', 'district', 'category', prepare_title, website, 'position', 'is_active') 
    ordering = ['position']
    list_filter = ('is_active', )
    list_select_related = True 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'division':
            kwargs['queryset'] = City.actives.order_by('slug')
        if db_field.name == 'district':
            kwargs['queryset'] = District.actives.order_by('slug')
        return super(self.__class__, self).formfield_for_foreignkey(db_field, request, **kwargs)

class FeatureSiteAdmin(admin.ModelAdmin):
    list_display = ('prepare_site', 'city', 'position', 'style', 'is_active')

    def prepare_site(self, obj):
        name = Website.objects.values('name').get(pk=obj.site_id)['name']
        return name 
    prepare_site.short_description = '站点'

class ClientReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'submit_date', 'is_remove', 'ip_address')

class JinPinDealAdmin(admin.ModelAdmin):
    list_display = ('deal_id', 'category', 'city')
    list_filter = ('category', )
    search_fields = ('city__slug',)

admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(CityConstrain, CityConstrainAdmin) 
admin.site.register(CustomCityDeal, CustomCityDealAdmin)
admin.site.register(CustomCategoryDeal, CustomCategoryDealAdmin)
admin.site.register(CustomDistrictDeal, CustomDistrictDealAdmin)
admin.site.register(CustomCategoryByDistrict, CustomCategoryByDistrictAdmin)
admin.site.register(FeatureSite, FeatureSiteAdmin)
admin.site.register(CarouselAd)
admin.site.register(ActivityDeal)
admin.site.register(MiniCategory)
admin.site.register(MiniItem)
admin.site.register(ClientReview0, ClientReviewAdmin)
admin.site.register(ClientReview1, ClientReviewAdmin)
admin.site.register(ClientReview2, ClientReviewAdmin)
admin.site.register(ClientReview3, ClientReviewAdmin)
admin.site.register(ClientReview4, ClientReviewAdmin)
admin.site.register(ClientReview5, ClientReviewAdmin)
admin.site.register(ClientReview6, ClientReviewAdmin)
admin.site.register(ClientReview7, ClientReviewAdmin)
admin.site.register(ClientReview8, ClientReviewAdmin)
admin.site.register(ClientReview9, ClientReviewAdmin)
admin.site.register(AppCategory)
admin.site.register(AppItem)
admin.site.register(JinPinDeal, JinPinDealAdmin)
