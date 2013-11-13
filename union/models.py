#! -*- coding:utf-8 -*-
from django.db import models
from guider.models import Website, City, Category

class AdSitePositionManager(models.Manager):
    def active(self):
        return self.get_query_set().filter(is_active=True)

# Create your models here.
class AdSitePosition(models.Model):
    site        = models.IntegerField(u'站点')
    start_date  = models.DateField(u'开始时间')
    expire_date = models.DateField(u'终止时间')
    division    = models.ForeignKey(City, verbose_name=u'城市')
    category    = models.ForeignKey(Category, verbose_name='分类')
    is_active   = models.BooleanField(u'是否激活', default=True)
    priority    = models.IntegerField(u'优先级', default=0, blank=True, null=True)
    position    = models.IntegerField(u'位置', help_text="特别推荐(0), 图片广告(>=1)")
    objects     = AdSitePositionManager()

    class Meta:
        db_table = 'adsiteposition'
        verbose_name = '广告站点位置'
        verbose_name_plural = '广告站点位置'
