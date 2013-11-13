from django.conf import settings
from tuangou.guider import models

def get_review_partition(id, module=models, kls=models.DealReview):
    mod = id % 10
    model_name = kls.__name__+ str(mod)
    return getattr(models, model_name)

def get_review_models(modules=models, kls=models.DealReview):
    review_models = [getattr(modules, kls.__name__+str(i)) for i in xrange(10)]
    return review_models
    
