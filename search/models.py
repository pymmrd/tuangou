from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class SearchTerm(models.Model):
    q = models.CharField(max_length=50)
    tracking_id = models.CharField(max_length=50, default='')
    search_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null=True)
        
    class Meta:
        db_table = 'searchterm'

    def __unicode__(self):
        return self.q

