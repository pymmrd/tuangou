# -*- coding: utf-8 -*-
#from django
from django.db import models
from django.contrib.auth.models import User
#from project
from tuangou.guider.models import ReDeal

# Create your models here.
class DealWish(models.Model):
    user = models.ForeignKey(User)
    deal = models.ForeignKey(ReDeal)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = u"收藏"
        verbose_name_plural = u"收藏"
        db_table = 'dealwish'

    def __unicode__(self):
        return '%s-%s' % (self.user.username, self.deal.title)

