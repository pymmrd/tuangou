from django.db import models
from django.contrib.auth.models import User
from tuangou.guider.models import ReDeal, City

# Create your models here.
class PageView(models.Model):
    class Meta:
        abstract = True

    date = models.DateTimeField(auto_now=True)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null=True)
    tracking_id = models.CharField(max_length=50, default='')

class DealView(PageView):
    city = models.ForeignKey(City, null=True)
    deal = models.ForeignKey(ReDeal)

    class Meta:
        db_table = 'dealview'
