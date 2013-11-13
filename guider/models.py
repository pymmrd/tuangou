# -*- coding:utf-8 -*-
import sys
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, timedelta, date, time

NONE = 0
NORMAL = 1 
ENHANCE = 2
OTHER = 3
SPIDER_TYPE = (
    (NORMAL, 'Normal'),
    (ENHANCE, 'Enhance'),
    (OTHER,  'Other'),
    (NONE,'None'),
)

class ActiveManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)

class ActiveObject(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(is_active=True)

class FamousSite(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(is_famous=True)

# Create your models here.
class Website(models.Model):
    name = models.CharField(u'名称(中文)', max_length=50, 
                                   unique=True, db_index=True)
    slug = models.SlugField(u'名称(拼音)', db_index=True, max_length=20)
    url = models.URLField(u'地址', unique=True, db_index=True, verify_exists=False)
    deal_api = models.CharField('活动API', blank=True, max_length=200)
    city_api = models.URLField('城市API', blank=True, verify_exists=False)
    opened_city = models.ManyToManyField('City', verbose_name=u'开通城市',
                                        blank=True, null=True, db_index=True)
    deal_crawl_type = models.IntegerField(u"活动爬虫类型", 
                                            choices=SPIDER_TYPE, default=NORMAL)
    city_crawl_type = models.IntegerField(u"城市爬虫类型", 
                                            choices=SPIDER_TYPE, default=NORMAL)
    is_active = models.BooleanField(u"是否有效", default=True)
    city_api_tags = models.CharField(u"城市API节点", max_length=100, 
                                                     blank=True, db_index=True)
    date_fmt = models.CharField(u"日期格式", max_length=100, blank=True)
    created_date = models.DateTimeField(u"创建日期", auto_now_add=True)
    weight = models.IntegerField(u"权重", blank=True, null=True, db_index=True)
    is_famous = models.BooleanField(u"是否名站", default=False, db_index=True)
    api_tags_active = models.BooleanField(u'激活API节点', default=False)
    objects = models.Manager()
    actives = ActiveObject()
    famouses = FamousSite()

    class Meta:
        verbose_name = '收入站点'
        verbose_name_plural = '收入站点'
        db_table = 'website1'
        ordering =['-created_date']

    def __unicode__(self):
        return "%s-%s" % (self.name, self.slug)

class CityAPIName(models.Model):
    website = models.ManyToManyField(Website, related_name='cityapi', 
                                    verbose_name=u'站点', db_index=True)
    api_name = models.CharField( max_length=100, 
                                    verbose_name=u'后缀名', db_index=True)
    is_active = models.BooleanField(default=True, verbose_name=u'是否有效')

    class Meta:
        verbose_name = u'站点API(后缀)'
        verbose_name_plural = u'站点API(后缀)'
        db_table = 'cityapiname'

    def __unicode__(self):
        return self.api_name

class AreaBase(models.Model):
    name = models.CharField(u'名字', max_length=30, db_index=True)
    slug = models.CharField(u'名字(拼音)', 
                                    max_length=20, db_index=True)
    meta_keywords = models.CharField(u'元关键字', 
                                        max_length=300, blank=True)
    meta_description = models.CharField(u'元描述', max_length=350, blank=True)
    is_active = models.BooleanField(u'是否有效', default=False)

    class Meta:
        abstract = True
        
class City(AreaBase):
    is_hot = models.BooleanField(u'是否是热门城市', default=False)
    created_date = models.DateTimeField(u"创建日期", auto_now_add=True)
    objects = models.Manager()
    actives = ActiveObject()

    class Meta:
        ordering = ['-created_date']
        verbose_name = u'城市'
        verbose_name_plural = u'城市'
        db_table = 'city'

    def __unicode__(self):
        return self.name

class District(AreaBase):
    parent = models.ForeignKey('self', verbose_name='父区域', 
                            related_name='children', null=True, blank=True)
    level = models.IntegerField(verbose_name= u'等级', blank=True,
                                default=0, db_index=True, editable=False)
    ancestors = models.ManyToManyField('self', symmetrical=False, 
        editable=False, related_name="descendants",  db_index=True,
                                                  verbose_name=u'子分类')
    city = models.ForeignKey(City, verbose_name=u'城市', 
                            related_name='districts', null=True, blank=True)
    objects = ActiveManager()

    class Meta:
        verbose_name = u'商区'
        verbose_name_plural = u'商区'
        db_table = 'district'
        ordering = ['slug']

    def save(self, ancestors=None, *args, **kwargs):
        if ancestors is None:
            ancestors = []
        if self.parent and self.id:
            assert self.parent not in self.descendants.all(), "prevent loop reference"

        if self.parent:
            self.level = self.parent.level + 1 
        else:
            self.level = 0 
        super(self.__class__, self).save(*args, **kwargs)
        self.ancestors.clear()
        if self.parent:
            if not ancestors:
                ancestors = list(self.parent.ancestors.all())
                ancestors.extend([self.parent,])
            self.ancestors.add(*ancestors)
        childs_ancestors = ancestors.extend([self, ])
        for child in self.children.all():
            child.save(ancestors=childs_ancestors)

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if type(L) != type([]): return [L]
        if L == []: return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node, only_active=False):
        children = []
        children.append(node)
        for child in node.children.active():
            if child != self:
                children_list = self._recurse_for_children(child, only_active=only_active)
                children.append(children_list)
        return children

    def get_active_children(self, include_self=False):
        """
        Gets a list of all of the children categories which have active products.
        """
        return self.get_all_children(only_active=True, include_self=include_self)

    def get_all_children(self, only_active=False, include_self=False):
        """
        Gets a list of all of the children categories.
        """
        children_list = self._recurse_for_children(self, only_active=only_active)
        if include_self:
            ix = 0
        else:
            ix = 1
        flat_list = self._flatten(children_list[ix:])
        return flat_list

    def get_active_children_pk(self, include_self=False):
        children = self.get_active_children(include_self=include_self)
        childs = [obj.pk for obj in children]
        return childs

    def __unicode__(self):
        return self.name

class Shop(models.Model):
    name = models.CharField(u'商店', max_length=100
                                ,unique=True, db_index=True)
    slug = models.SlugField(u'商店(拼音)', max_length=50, blank=True)
    url = models.CharField(u'网址', max_length=100, blank=True)
    telephone = models.CharField(u'电话', max_length=300, blank=True)
    address = models.CharField(u'地址', max_length=400, blank=True)
    longitude = models.CharField(u'经度', max_length=50, blank=True)
    latitude = models.CharField(u'纬度', max_length=50, blank=True)
    is_active = models.BooleanField(u'是否激活', default=True)
    created_date = models.DateTimeField(u'创建时间', auto_now=True)

    class Meta:
        verbose_name = u'商铺'
        verbose_name_plural = u'商铺'
        db_table = 'shop'
        ordering = ['-created_date']

    def __unicode__(self):
        return  '%s--->%s' % (self.pk, self.name)

class Deal_Shop_City_District(models.Model):
    deal_id = models.IntegerField(verbose_name='活动ID', db_index=True)
    shop = models.ForeignKey(Shop, verbose_name='商店', blank=True, null=True)
    city = models.ForeignKey(City, verbose_name='城市', blank=True, null=True)
    district = models.ForeignKey(District, verbose_name=u'商区', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=True)
    objects = models.Manager()
    actives = ActiveObject()

    class Meta:
        db_table = 'deal_shop_city_district'
        verbose_name = u'活动ER'
        verbose_name_plural = u'活动ER'
        unique_together = ('deal_id', 'shop', 'city', 'district')

class CategoryManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs).order_by('order')

class Category(models.Model):
    title = models.CharField(u'标题', max_length=50, db_index=True, unique=True)
    slug = models.SlugField(u"标题(拼音)", max_length=50, db_index=True)
    parent = models.ForeignKey('self', related_name='children', 
            verbose_name=u'父分类', null=True, blank=True)
    ancestors = models.ManyToManyField('self', symmetrical=False, 
        editable=False, related_name="descendants",  db_index=True,
                                                  verbose_name=u'子分类')
    level = models.IntegerField(verbose_name= u'等级', blank=True,
                                default=0, db_index=True, editable=False)
    order = models.IntegerField(verbose_name=u'顺序', blank=True, 
                                                default=0, db_index=True)
    meta_keywords = models.CharField(u'元关键字', max_length=300, blank=True)
    meta_description = models.CharField(u'元描述', max_length=350, blank=True)
    is_active = models.BooleanField(default=True)
    objects = CategoryManager()

    class Meta:
        verbose_name = u"分类"
        verbose_name_plural = u"分类"
        db_table = 'category'
        ordering = ['slug']

    def path(self, seq=" > ", field="title"):
        path = [o[field] for o in self.ancestors.all().order_by('level').values(field)]
        path.extend([getattr(self, field),])
        return seq.join(path)

    def active_products(self, include_children=False, **kwargs):
        if not include_children:
            qry = self.redeal_set.all()
        else:
            cats = self.get_all_children(include_self=True)
            qry = ReDeal.nonexpires.filter(category__in=cats)
        return qry

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if type(L) != type([]): return [L]
        if L == []: return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node, only_active=False):
        children = []
        children.append(node)
        for child in node.children.active():
            if child != self:
                children_list = self._recurse_for_children(child, only_active=only_active)
                children.append(children_list)
        return children

    def get_active_children(self, include_self=False):
        """
        Gets a list of all of the children categories which have active products.
        """
        return self.get_all_children(only_active=True, include_self=include_self)

    def get_all_children(self, only_active=False, include_self=False):
        """
        Gets a list of all of the children categories.
        """
        children_list = self._recurse_for_children(self, only_active=only_active)
        if include_self:
            ix = 0
        else:
            ix = 1
        flat_list = self._flatten(children_list[ix:])
        return flat_list

    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p)
            if p != self:
                more = self._recurse_for_parents(p)
                p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list

    def parents(self):
        return self._recurse_for_parents(self)

    def get_active_children_pk(self, include_self=False):
        children = self.get_active_children(include_self)
        childs = [obj.pk for obj in children]
        return childs

    @classmethod
    def top_level(self, *args, **kw):
        return self.objects.filter(is_active=True, parent__isnull=True, *args, **kw)

    def save(self, ancestors=None):
        if ancestors is None:
            ancestors = []
        if self.parent and self.id:
            assert self.parent not in self.descendants.all(), "prevent loop reference"

        if self.parent:
            self.level = self.parent.level + 1 
        else:
            self.level = 0 
        super(self.__class__, self).save()
        self.ancestors.clear()
        if self.parent:
            if not ancestors:
                ancestors = list(self.parent.ancestors.all())
                ancestors.extend([self.parent,])
            self.ancestors.add(*ancestors)
        childs_ancestors = ancestors.extend([self, ])
        for child in self.children.all():
            child.save(ancestors=childs_ancestors)

    def __unicode__(self):
        return self.path()

class MatchWord(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'分类', 
                                            related_name='matchwords')
    word = models.CharField(u'关键字', max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(u'是否有效', default=True)

    class Meta:
        db_table = 'matchword'
        verbose_name = '关键字'
        verbose_name_plural = '关键字'

    def __unicode__(self):
        return self.word

class DealBase(models.Model):
    category = models.ForeignKey(Category, null=True, blank=True)
    title = models.CharField(u'标题', max_length=500)
    image = models.ImageField(u'图片', upload_to='%Y/%m/%d')
    thumbnail = models.ImageField(u'缩略图', upload_to='%Y/%m/%d')
    start_date = models.DateTimeField(u'开始时间')
    end_date = models.DateTimeField(u'结束时间', db_index=True)
    deal_url = models.URLField(u'活动地址', verify_exists=False)
    price = models.DecimalField(u'价格', decimal_places=2, max_digits=9, db_index=True)
    origin_price = models.DecimalField(u'原价', decimal_places=2, max_digits=9,
                                            blank=True, null=True)
    discount  = models.DecimalField(u"折扣", decimal_places=2, 
                                            max_digits=9, db_index=True)
    bought = models.IntegerField(u"购买", blank=True, null=True)
    division  =  models.ManyToManyField(City, verbose_name=u'城市', db_index=True)
    website = models.ForeignKey(Website ,verbose_name=u'站点') 
    district = models.ManyToManyField(District, verbose_name=u'商区', 
                                    db_index=True, blank=True, null=True)
    description = models.TextField(u'描述', blank=True, null=True)
    md5sum = models.CharField(max_length=32, unique=True)
    created_date = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_active = models.BooleanField(u'是否激活', default=True)
    
    class Meta:
        abstract = True
    
class NonExpireDealManager(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(end_date__gte=datetime.combine(date.today(), time(23, 59, 59)))

class NewDealManager(models.Manager):
    def get_query_set(self):
        return super(self.__class__, self).get_query_set().filter(created_date__gte=datetime.combine(date.today(), time(0, 0, 0)))

class Deal(DealBase):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    objects = models.Manager()
    nonexpires = NonExpireDealManager()
    news = NewDealManager()

    class Meta:
        ordering = ['-created_date']
        verbose_name = u'团购活动'
        verbose_name_plural = u'团购活动'
        db_table = 'deal'

    def __unicode__(self):
        return self.title

class BaseChart(models.Model):
    deal = models.ForeignKey('ReDeal', verbose_name=u'团购活动')
    city = models.ForeignKey(City, verbose_name=u'城市')
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class SellerChart(BaseChart):
    quantity = models.IntegerField(u'销售数量')
 
    class Meta:
        verbose_name = u'销量排行'
        verbose_name_plural = u'销量排行'
        db_table = 'sellerchart'
        ordering = ['-quantity']

    def __unicode__(self):
        return "%s-%s" % (self.quantity, self.deal.title)

class ViewChart(BaseChart):
    rank = models.IntegerField(u'排名')

    class Meta:
        verbose_name = u'点击排行'
        verbose_name_plural = u'点击排行'
        db_table = 'viewchart'

    def __unicode__(self):
        return "%s-%s" % (self.rank, self.deal.title)

class DealFieldMap(models.Model):
    FIELD_CHOICE = (
        ('price', 'price'),
        ('title', 'title'),
        ('image', 'image'),
        ('bought', 'bought'),
        ('deal_url', 'deal_url'),
        ('end_date', 'end_date'),
        ('division', 'division'),
        ('discount', 'discount'),
        ('district', 'district'),
        ('start_date', 'start_date'),
        ('origin_price', 'origin_price'),
        ('description', 'description'),
        ('shop',  'shop'),
        ('shop_url', 'shop_url'),
        ('shop_lng', 'shop_lng'),
        ('shop_lat', 'shop_lat'),
        ('address', 'address'),
        ('telephone', 'telephone')
    )
    node = models.CharField(u"节点", max_length=50, db_index=True)
    origin_field = models.CharField(u"列名", max_length=50, 
                                choices=FIELD_CHOICE, db_index=True)
    website = models.ForeignKey(Website, verbose_name=u"站点", related_name='deal_map')

    class Meta:
        verbose_name = u'列名与节点映射'
        verbose_name_plural = u'列名与节点映射'
        db_table = 'dealfieldmap'

    def __unicode__(self):
        return  "%s - %s" % (self.origin_field, self.node)

class ReDeal(DealBase):
    is_ad = models.BooleanField(u'是否广告', default=False)
    objects = models.Manager()
    nonexpires = NonExpireDealManager()
    news = NewDealManager()
    class Meta:
        verbose_name = u'团购活动'
        verbose_name_plural = u'团购活动'
        db_table = 'redeal'

    def __unicode__(self):
        return self.title

class DealReview(models.Model):
    user = models.ForeignKey(User, verbose_name=u'用户') 
    deal = models.ForeignKey(ReDeal, verbose_name=u'团购')
    comment = models.TextField(u'评论')
    submit_date = models.DateTimeField(u'评论日期', auto_now_add=True)
    ip_address = models.IPAddressField(u'IP地址', blank=True, null=True)
    is_remove = models.BooleanField(u'是否删除', default=False)
    
    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = u'评论'
        abstract = True

    def __unicode__(self):
        return '%s-->%s' % (self.pk, self.user.username)

def create_review_models(base): 
    import sys
    _current_module = sys.modules[__name__]
    for i in xrange(0, 10):
        name = DealReview.__name__ + str(i)
        if _current_module.__dict__.has_key(name):
            continue
        new_model = type(name, (base,), {'__module__':__name__})
        new_model._meta.db_table = name.lower()
        _current_module.__dict__[name] = new_model
create_review_models(DealReview)

class FriendLink(models.Model):
    link = models.URLField(u'链接',verify_exists=True)
    logo = models.URLField(u'logo链接', verify_exists=True)
    name = models.CharField(u'名字', max_length=255)
    is_active = models.BooleanField(u'是否激活', default=True)
    objects = ActiveManager()

    class Meta:
        db_table = 'friendlink'
        verbose_name = u'友情链接'
        verbose_name_plural = u'友情链接'

    def __unicode__(self):
        return self.name

def _listen():
    from tuangou.guider import watchers
    from django.db.models.signals import pre_delete, post_delete, post_save
    pre_delete(watchers.deal_pre_delete, sender=ReDeal)
