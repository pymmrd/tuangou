from django.conf import settings
from tuangou.commerce import models

def get_review_partition(id, module=models, kls=models.ClientReview):
    mod = id % 3
    model_name = kls.__name__ + str(mod)
    return getattr(models, model_name)
