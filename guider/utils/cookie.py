from django.conf import settings

def cookie_process(request, current_city):
    request.session[settings.COOKIE_CITY_NAME] = current_city
    
