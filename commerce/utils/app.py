#from pylib
import os
from datetime import datetime
from collections import defaultdict
#from django
from django.conf import settings
#from project
from tuangou.utils import get_log_path, load_pickle_data, dump_data

def get_access_dir(dir_name, d=None, path=settings.LOG_PATH):
    return get_log_path(dir_name, d, path)

def get_log_file(vcode, d=None):
    sub_dir = get_access_dir('commerce', d)
    filename = settings.APP_CLICK_LOG % vcode
    log_file = os.path.join(sub_dir, filename) 
    return log_file

def gen_app_access_log(request, url):
    #ip, url, 'date', 'username'
    username = None
    if request.user.is_authenticated():
        username = request.user.username
    log_file = get_log_file()
    with open(log_file, 'a') as f:
        print >> f, '%s\t%s\t[%s]\t%s' % (request.META.get('REMOTE_ADDR', None), url,
            datetime.today().strftime('%Y-%m-%d %H:%M:%S'), username)

def gen_app_audit_data(vcode, position):
    pick_data = defaultdict(int)
    log_file = get_log_file(vcode)
    if os.path.exists(log_file):
        pick_data = load_pickle_data(log_file)
    if position in pick_data:
        pick_data[position] += 1
    else:
        pick_data[position] = 1
    dump_data(log_file, pick_data)

def get_app_audit_data(vcode, d):
    pick_data = {}
    log_file = get_log_file(vcode, d)
    if os.path.exists(log_file):
        pick_data = load_pickle_data(log_file)
    return pick_data
