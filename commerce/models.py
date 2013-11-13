# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date, time
from guider.models import City, Category, District

ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
TYPE_CHOICE = (
    (ONE, 'Normal'),
    (TWO, 'Multimedia'),
    (THREE, 'Mini'),
)

class AdBase(models.Model):
    PRIORITY_CHOICE = (
        (ONE, 'ONE'),
        (TWO, 'TWO'),
        (THREE, 'THREE'),
        (FOUR, 'FOUR'),
        (FIVE, 'FIVE'),
    )
    show_times = models.IntegerField(u'展示次数', blank=True, null=True)
    start_time = models.DateTimeField(u'开始时间', blank=True, null=True)
    expire_time = models.DateTimeField(u'结束时间', blank=True, null=True)
    start_time_per_day = models.DateTimeField(u'每天开始时间', blank=True, null=True)
    expire_time_per_day = models.DateTimeField(u'每天结束时间', blank=True, null=True)
    show_times_per_day = models.IntegerField(u'每天展示次数', blank=True, null=True)
    timedelta = models.IntegerField(u'间隔展示天数', blank=True, null=True)
    sub_total = models.IntegerField(u'部分和', default=0, blank=True, null=True)
    is_active = models.BooleanField(u'是否有效', default=True)
    priority = models.IntegerField(u'优先级', default=FIVE, choices=PRIORITY_CHOICE, db_index=True)

    class Meta:
        abstract = True

class ActiveManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)

# Create your models here.
class Advertisement(AdBase):
    id = models.IntegerField(u'广告标识', primary_key=True)
    width = models.IntegerField(u'宽度')
    height = models.IntegerField(u'高度')
    type = models.IntegerField(u'类型', choices=TYPE_CHOICE, default=ONE) 
    tray = models.BooleanField(u'闪烁', default=False)
    prweb = models.BooleanField(u'是否纯网页', default=False)
    dragarea = models.CharField(u'拖动区域', blank=True, max_length=50, help_text='此参数为可选参数，以prweb=1时为基准，参数形式为(x,y,w,h). (x, y)相对边框左上角坐标， (w, h)：宽度和高度坐标')
    template = models.CharField(u'模板', max_length=100, blank=True)
    dispatch_city = models.ManyToManyField(City, blank=True, null=True, verbose_name=u'派发城市')
    objects = ActiveManager()

    class Meta:
        db_table = 'advertisement'
        verbose_name = u'客户端广告'
        verbose_name_plural = u'客户端广告'

    def __unicode__(self):
        return str(self.id)

class CityConstrain(AdBase):
    ad = models.ForeignKey(Advertisement, related_name='cityconstrain', verbose_name=u'广告')
    division = models.ForeignKey(City, blank=True, null=True, verbose_name=u'城市')
    objects = ActiveManager()

    class Meta:
        db_table = 'cityconstrain'
        verbose_name = u'客户端广告约束'
        verbose_name_plural = u'客户端广告约束'
        
    def __unicode__(self):
        return u'%s-->%s' % (self.ad.id, self.division.name)

class DispatchManager(models.Manager):
    def dispatch(self, **kwargs):
        return self.filter(created_date__gte=datetime.combine(date.today(), time(0, 0, 0)), **kwargs)
    
class DispatchRecord(models.Model):
    mac = models.CharField('MAC', max_length=32, db_index=True)
    ad = models.ForeignKey(Advertisement, verbose_name='广告')
    division = models.ForeignKey(City, blank=True, null=True, verbose_name='城市')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    objects = DispatchManager()
    class Meta:
        db_table = 'dispatchrecord'
        verbose_name = u'广告分发记录'
        verbose_name_plural = u'广告分发记录'

class StoreList(models.Model):
    name = models.CharField(u'名字', max_length=120)
    domain = models.CharField(u'域名', max_length=120)
    is_active = models.BooleanField(u'是否激活', default=True)
    objects = ActiveManager()

    class Meta:
        db_table = 'storelist'
        verbose_name = u'电商列表'
        verbose_name_plural = u'电商列表'
    
    def __unicode__(self):
        return self.name
    
class CustomDeal(models.Model):
    NORMAL = 1
    FEATURE = 2
    ACTIVITY = 3
    MINI = 4
    ATTRIBUTE_CHOICE = (
        (NORMAL, '分类广告'),
        (FEATURE, '特别推荐'),
        (ACTIVITY, '活动广告'),
        (MINI, '迷你窗'),
    )
    deal_id = models.IntegerField(u'活动ID', db_index=True)
    division = models.ForeignKey(City, verbose_name=u'城市')
    position = models.IntegerField(u'位置', db_index=True)
    is_active = models.BooleanField(u'是否有效', default=True)
    attribute = models.IntegerField(u'属性', choices=ATTRIBUTE_CHOICE, default=NORMAL)

    class Meta:
        abstract = True

class ActivityDeal(models.Model):
    deal_id = models.IntegerField(u'活动ID', db_index=True)
    division = models.ForeignKey(City, verbose_name=u'城市', blank=True, null=True)
    position = models.IntegerField(u'位置', db_index=True)
    is_active = models.BooleanField(u'是否有效', default=True)

    class Meta:
        verbose_name = '活动专区广告'
        verbose_name_plural = '活动专区广告'
        db_table = 'activitydeal'
        ordering = ['position']
    
    def __unicode__(self):
        return '%s-%s' % (self.deal_id, self.position)

class CustomCityDeal(CustomDeal):
    class Meta:
        verbose_name = '城市页面广告'
        verbose_name_plural = '城市页面广告' 
        db_table = 'customcitydeal'

class CustomCategoryDeal(CustomDeal):
    category = models.ForeignKey(Category, verbose_name=u'分类')

    class Meta:
        verbose_name = '分类页面广告'
        verbose_name_plural = '分类页面广告'
        db_table = 'customcategorydeal'

class CustomDistrictDeal(CustomDeal):
    district = models.ForeignKey(District, verbose_name=u'商区')
    class Meta:
        verbose_name = '商区页面广告'
        verbose_name_plural = '商区页面广告'
        db_table = 'customdistrictdeal'

class CustomCategoryByDistrict(CustomDeal):
    category = models.ForeignKey(Category, verbose_name=u'分类')
    district = models.ForeignKey(District, verbose_name=u'商区')

    class Meta:
        db_table = 'customcategorybydistrict'
        verbose_name = '商区分类页面广告'
        verbose_name_plural = '商区分类页面广告'

class MiniCategory(models.Model):
    name = models.CharField(u'名称(中文)', max_length=50,
                                   unique=True, db_index=True)
    slug = models.SlugField(u'名称(拼音)', db_index=True, max_length=20)
    url = models.CharField(u'链接', max_length=225,  blank=True)
    is_active = models.BooleanField(u'激活', default=True)
    order = models.IntegerField(u'顺序', default=0)
    objects = ActiveManager()

    class Meta:
        db_table = 'minicategory'
        verbose_name = u'迷你分类'
        verbose_name_plural = u'迷你分类'

    def __unicode__(self):
        return self.name

class MiniItem(models.Model):
    category = models.ForeignKey(MiniCategory, verbose_name='分类')
    title = models.CharField(u'标题', max_length=255)
    image_url = models.URLField(u'图片地址', verify_exists=True)
    url = models.URLField(u'链接', verify_exists=False)
    position = models.IntegerField(u'位置')
    is_active = models.BooleanField(u'激活', default=True)
    objects = ActiveManager()
    class Meta:
        db_table = 'miniitem'
        verbose_name = u'迷你商品'
        verbose_name_plural = u'迷你商品'

    def __unicode__(self):
        return self.title

class JinPinDeal(models.Model):
    deal_id = models.IntegerField(u'活动ID', db_index=True)
    category = models.ForeignKey(MiniCategory, verbose_name='分类', \
                    blank=True, null=True)
    city = models.ForeignKey(City, verbose_name='城市')
    position = models.IntegerField(u'位置', default=0)
    is_active = models.BooleanField(u'是否有效', default=True)

    class Meta:
        db_table="jinpindeal"
        verbose_name = '精品团购'
        verbose_name_plural = '精品团购'

    def __unicode__(self):
        return "%s-%s" % (self.deal_id, self.city.name)

class FeatureSite(models.Model):
    site_id = models.IntegerField(u'站点ID', db_index=True)
    city = models.ForeignKey(City, verbose_name=u'城市')
    position = models.IntegerField(u'位置', db_index=True)
    is_active = models.BooleanField(u'是否有效', default=True)
    style = models.CharField(u'显示样式', max_length=100)
    class Meta:
        db_table = 'featuresite'
        verbose_name = '推荐站点'
        verbose_name_plural = '推荐站点'

class CarouselAd(models.Model):
    category = models.ForeignKey(MiniCategory, verbose_name='分类', blank=True, null=True)
    title = models.CharField(u'商户', max_length=255, blank=True)
    image = models.ImageField(u'图片', upload_to='commerce/carousel')
    url = models.URLField(u'链接', verify_exists=False)
    is_active = models.BooleanField(u'是否有效', default=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)
    objects = ActiveManager()

    def __unicode__(self):
        return 'carousel-%s' % self.pk

    class Meta:
        db_table = "carouselad"
        verbose_name = '广告轮播'
        verbose_name_plural = '广告轮播'

class AppCategory(models.Model):
    VCODE_CHOICE = ( 
        ('01', u'游戏'),
        ('02', u'音乐'),
        ('03', u'视频'),
        ('04', u'阅读'),
        ('05', u'工具'),
    )   
    title = models.CharField(u'标题', max_length=50)
    name = models.CharField(u'名称(中文)', max_length=50)
    vcode = models.CharField(u'标识符', choices=VCODE_CHOICE, max_length=2, db_index=True)
    is_active = models.BooleanField(u'是否激活', default=True)
    objects = ActiveManager()

    class Meta:
        db_table = 'appcategory'
        verbose_name = u'App分类'
        verbose_name_plural = u'App分类'

    def __unicode__(self):
        return '%s-%s' % (self.name, self.vcode)

class AppItem(models.Model):
    category = models.ForeignKey(AppCategory, verbose_name='分类', blank=True, null=True)
    title = models.CharField(u'标题', max_length=255, blank=True)
    image = models.ImageField(u'图片', upload_to='commerce/app')
    url = models.CharField(u'链接', max_length=255, help_text='去除链接前面的http://前缀')
    width = models.IntegerField(u'宽度')
    height = models.IntegerField(u'高度')
    position = models.IntegerField(u'位置')
    is_active = models.BooleanField(u'是否有效', default=True)
    objects = ActiveManager()
    
    class Meta:
        db_table = 'appitem'
        verbose_name = u'App元素'
        verbose_name_plural = u'App元素'

    def __unicode__(self):
        return self.title

class ClientReview(models.Model):
    user = models.ForeignKey(User, verbose_name=u'用户') 
    comment = models.TextField(u'评论')
    submit_date = models.DateTimeField(u'评论日期', auto_now_add=True)
    ip_address = models.IPAddressField(u'IP地址', blank=True, null=True)
    is_remove = models.BooleanField(u'是否删除', default=False)

    class Meta:
        verbose_name = u'客户端评论'
        verbose_name_plural = u'客户端评论'
        abstract = True

def create_review_models(base):
    import sys
    _current_module = sys.modules[__name__]
    for i in xrange(0, 10):
        name = ClientReview.__name__ + str(i)
        if _current_module.__dict__.has_key(name):
            continue
        new_model = type(name, (base,), {'__module__': __name__})
        new_model._meta.db_table = name.lower()
        _current_module.__dict__[name] = new_model
create_review_models(ClientReview)
