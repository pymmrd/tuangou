#from pylib
import sys
import os
import time
import fcntl
import traceback
import cPickle as pickle 
from datetime import date, timedelta, datetime
#from django
from django.conf import settings
from django.http import HttpResponse
from django.utils.http import cookie_date
from tuangou.utils.location import get_current_city

def load_pickle_data(name, mode='r'):
    with open(name, mode) as f:
        pick_data = pickle.load(f)
    return pick_data

def dump_data(name, data, mode='w'):
    f = open(name, mode)
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        pickle.dump(data, f)
        f.flush()
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()

def app_error_log(func=None, LOG_FILE=settings.ERROR_LOG_FILE):
    def wrapper(func):
        def process(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, 
                                         exc_value, 
                                         exc_tb, 
                                         limit=7, 
                                         file=open(get_log_file(LOG_FILE), 'a'))
            raise e
        return process
    if func is None:
        def decorator(func):
            return wrapper(func)
        return decorator
    return wrapper(func)

def set_cookie(func):
    def process(*args, **kwargs):
        response = func(*args, **kwargs)
        request = args[0]
        city  = get_current_city(request)
        session_city = city.slug
        if session_city:
            max_age = request.session.get_expiry_age()
            expires_time = time.time() + max_age
            expires = cookie_date(expires_time)
            response.set_cookie(settings.CITY_COOKIE_NAME,
                        session_city, max_age=max_age,
                        expires=expires)
        return response
    return process

def get_log_file(filename):
    today = date.today()
    filename, ext = os.path.splitext(filename)
    filename = "%s_%s_%s_%s%s" % (filename, str(today.year), str(today.month), str(today.day), ext) 
    return filename 

def smart_unicode(s):
    if not isinstance(s, basestring):
        s = unicode(str(s))
    elif not isinstance(s, unicode):
        s = unicode(s, settings.DEFAULT_CHARSET, 'ignore')
    return s

def get_log_path(dir_name, d=None, path=settings.LOG_PATH):
    if d: 
        today = d
    else:
        today= date.today()
    log_path = os.path.join(path, '%s/%s/%s/%s' % (dir_name, str(today.year), str(today.month), str(today.day)))
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    return log_path

def get_lastday(d=None):
    if d:
        lastday = d - timedelta(days=1)
    else:
        lastday = datetime.today() - timedelta(days=1)
    return lastday
