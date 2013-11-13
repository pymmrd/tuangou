import os
import fcntl 
import operator
import cPickle as pickle
from django.conf import settings
from datetime import date, datetime
from tuangou.utils import get_log_path, load_pickle_data

PAGE_IDENTFIER = {'h': 'home', 'c': 'city', 'd': 'district', 'ca': 'category', 'da': 'dist-category'}
NORMAL_BLOCKS = ['a', 'b']

def get_audit_data_dir(d=None, dir_name=settings.AUDIT_DIR_NAME, path=settings.LOG_PATH):
    return get_log_path(dir_name=dir_name, d=d, path=path)

def get_audit_filename(area, flag='uv'):
    name, ext = os.path.splitext(settings.SITE_AUDIT_LOG_FILE)
    name = '%s_%s_%s%s' % (name, flag, area, ext)
    return name

def get_log_file(area, flag):
    try:
        page, area = area.split('_')
    except ValueError:
        log_path = get_audit_data_dir()
    else:
        page = PAGE_IDENTFIER[page]
        sub_dir = get_audit_data_dir()
        log_path = os.path.join(sub_dir, page)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
    name = get_audit_filename(area, flag)
    log_file = os.path.join(log_path, name)
    return log_file

def gen_audit_data(request, site_name, id,  area, r, flag=None):
    #ip #domain, 'refer', 'date'
    refer = r if r else None
    username = None
    if request.user.is_authenticated():
        username= request.user.username
    log_file = get_log_file(area, flag)
    with open(log_file, 'a') as f:
        print >> f, '%s\t%s\t[%s]\t%s\t%s\t%s\t%s' % (request.META.get('REMOTE_ADDR', None), request.COOKIES.get('uuid', None),
                                datetime.today().strftime('%Y-%m-%d %H:%M:%S'), site_name, refer, username, id)

def get_and_check_pickfile(d, pick_name, area,  dirname=None):
    audit_dir = get_audit_data_dir(d=d)
    audit_dir = os.path.join(audit_dir, dirname) if dirname else audit_dir 
    data_path = os.path.join(audit_dir, pick_name)
    if area in NORMAL_BLOCKS:
        return data_path, True
    else:
        return audit_dir, False

def get_normal_pickfile(path):
    pv_dict=load_pickle_data(path)
    return pv_dict

def get_position_pickfile(path, area):
    pv_dict = uv_dict = {}
    if area.startswith('s'):
        uv_pick_name = '%s_%s.pk' % (area, 'pv')
        pv_pick_name = '%s_%s.pk' % (area, 'pv')
    elif area.startswith('b'):
        uv_pick_name = '%s_%s.pk' % (area, 'uv')
        pv_pick_name = '%s_%s.pk' % (area, 'uv')
    else:
        uv_pick_name = '%s_%s.pk' % (area, 'uv')
        pv_pick_name = '%s_%s.pk' % (area, 'pv')
    uv_data_path = os.path.join(path, uv_pick_name) 
    pv_data_path = os.path.join(path, pv_pick_name) 
    if os.path.exists(uv_data_path):
        uv_dict = load_pickle_data(uv_data_path)
    if os.path.exists(pv_data_path):
        pv_dict = load_pickle_data(pv_data_path)
    return pv_dict, uv_dict

def get_sub_pv_uv(pv_dict, uv_dict):
    pass
    try:
        sub_pv = pv_dict.pop('sub_pv')
    except KeyError:
        sub_pv = 0
    try:
        sub_uv  = uv_dict.pop('sub_uv')
    except KeyError:
        sub_uv = 0
    return sub_pv, sub_uv

def get_page_audit(page, d):
    items = []
    total = 0
    pick_name = settings.PAGE_COUNTER_FILE % page
    path = os.path.join(get_audit_data_dir(d), page)
    pick_file = os.path.join(path, pick_name)
    if os.path.exists(pick_file):
        with open(pick_file, 'r') as f:
            data = pickle.load(f)
        items = sorted(data.iteritems(), key=operator.itemgetter(0))
        total = sum (item['uv'] for key, item in items) 
    return items, total

def get_click_file(d=None):
    log_path = get_audit_data_dir(d)
    log_file = os.path.join(log_path, settings.CLICK_COUNTER_FILE)
    return log_file

def click_counter():
    log_file = get_click_file()
    try:
        f = open(log_file, 'r+')
    except IOError:
        f = open(log_file, 'w')
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        number = 1
        f.write('%s' % number)
        f.flush()
    else:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        number = int(f.readline().strip()) + 1
        f.seek(0)
        f.write('%s' % number)
        f.flush()
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
