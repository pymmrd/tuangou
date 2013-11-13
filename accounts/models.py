from django.db import models
from guider.models import City
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from hashlib import sha1 as sha
import random
import string


MALE = 1
FEMALE = 2
GENDER_CHOICE= (
    (MALE, 'male'),
    (FEMALE, 'female'),
)
class UserProfile(models.Model):
    user = models.ForeignKey(User)
    nickname = models.CharField(max_length=50)
    birthday = models.DateTimeField(blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True, choices=GENDER_CHOICE)
    division = models.ForeignKey(City, blank=True , null=True)
    image = models.ImageField(upload_to='%Y/%m/%d/profiles')
    raw_image = models.ImageField(upload_to='%Y/%m/%d/profiles')

_random_str = string.digits + string.ascii_lowercase
random.seed()

def _generate_random_key(length=20):
    '''Return a random key 40 letters length'''
    input_str = ''.join(
        [random.choice(_random_str) for i in range(1, length+1)])
    return sha(input_str).hexdigest()

EXPIRED_TIMEDELTA = timedelta(3) # 3 days

class TempKeyManager(models.Manager):
    def create_key(self, user, action_flag):
        '''Create a new temp key.'''
        # find a new security key code which is unique
        key_str = None
        while True:
            try:
                key_str = _generate_random_key()
                self.get(key=key_str)
            except ObjectDoesNotExist:
                break
        # create new sercurity key in datebase
        new_key = self.create(user=user, key=key_str, action_flag=action_flag)
        # remove old keys related to the (user, action_flag)
        keys = self.filter(user=user, action_flag=action_flag).exclude(key=key_str)
        for key in keys:
            key.delete()
        return new_key

    def authenticate(self, key_str):
        '''Authenticate key

        Return TempKey object if key_str is exact and not expired.
        Return None if key_str is not exact or expired.
        '''
        key = None
        try:
            key = self.get(key__exact=key_str,
                create_date__gt=datetime.now()-EXPIRED_TIMEDELTA)
        except ObjectDoesNotExist:
            pass
        return key    

class TempKey(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=128, unique=True)
    action_flag = models.CharField(max_length=256)
    create_date = models.DateTimeField(auto_now_add=True)
    objects = TempKeyManager()

    class Meta:
        db_table = "tempkey"

