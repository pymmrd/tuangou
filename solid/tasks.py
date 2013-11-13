from celery.decorators import task
from solid.process import solid

@task(ignore_result=True)
def solid_page(slug):
    from guider.utils.cache  import cache_city
    city = cache_city(slug)
    solid(city)
