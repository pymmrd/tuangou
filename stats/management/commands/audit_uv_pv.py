# -*- coding:utf-8 -*-
import os
import glob
from django.conf import settings
from optparse import make_option
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand, CommandError
from tuangou.utils import get_log_path, dump_data, get_lastday, load_pickle_data
from tuangou.stats.utils.audit_site import get_audit_data_dir, \
    get_audit_filename

NORMAL_BLOCKS = {'city': ['a', 'b']}
POSITION_BLOCKS = {'city': ['c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']}
PV_INTERVALS = 20 * 60
REFER_KEY = 'refer'

def get_position_pattern(path, page, flag):
    blocks = POSITION_BLOCKS[page]
    name, ext = os.path.splitext(settings.SITE_AUDIT_LOG_FILE)
    for block in blocks:
        pattern = '%s_%s_%s*' % (name, flag, block)
        if os.path.exists(path):
            file_pattern = os.path.join(path, pattern)
            yield file_pattern

def get_position_file(pattern):
    file_list = glob.glob(pattern)
    for fi in file_list:
        filename = fi.rsplit('/', 1)[-1]
        filename, ext = os.path.splitext(filename)
        position = filename.split('_')[-1]
        yield (fi, position)

def pv_audit(audit_dict, key, username, access_time):
    try:
        ident = audit_dict[key]
    except KeyError:
        audit_dict['pv'] +=1
        audit_dict[key] = {}
        audit_dict[key]['last_time'] = access_time
        audit_dict[key]['last_user'] = username
    else:
        last_user = ident['last_user']
        if last_user != username:
            audit_dict['pv'] += 1 
            ident['last_user'] = username
        else:
            last_time = ident['last_time'] 
            delta = last_time - access_time
            if delta.seconds > PV_INTERVALS:
                audit_dict['pv'] += 1 
            ident['last_time'] = access_time

def uv_audit(audit_dict, key, username): 
    try:
        ident = audit_dict[key]
    except KeyError:
        audit_dict['uv'] += 1
        audit_dict[key] = {}
        if username != 'None':
            audit_dict[key].setdefault('username', []).append(username)
    else:
        try:
            user_list = ident['username']
        except KeyError:
            audit_dict['uv'] += 1
        else:
            if username  not in user_list: 
                audit_dict['uv'] += 1
                ident.setdefault('username', []).append(username)

def audit_both_pv_and_uv(audit_dict, key, username, access_time):
    try:
        ident = audit_dict[key]
    except KeyError:
        audit_dict['pv'] += 1
        audit_dict['uv'] += 1
        audit_dict[key] = {}
        audit_dict[key]['last_time'] = access_time
        audit_dict[key]['last_user'] = username
        if username != 'None':
            audit_dict[key].setdefault('username', []).append(username)
    else:
        last_user = ident['last_user']
        if last_user != username:
            audit_dict['pv'] += 1 
            ident['last_user'] = username
        else:
            last_time = ident['last_time'] 
            delta = last_time - access_time
            if delta.seconds > PV_INTERVALS:
                audit_dict['pv'] += 1 
            ident['last_time'] = access_time
        try:
            user_list = ident['username']
        except KeyError:
            audit_dict['uv'] += 1
        else:
            if username  not in user_list: 
                audit_dict['uv'] += 1
                ident.setdefault('username', []).append(username)
            
def refer_audit(audit_dict, key, refer):
    try:
        audit_dict[key][refer]
    except KeyError:
        audit_dict[key][refer] = 1
    else:
        audit_dict[key][refer] += 1

def read_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                items = line.split('\t')
                id = items[-1]
                site_name = items[-4]
                key = (items[0], items[1])
                refer = items[-3]
                username = items[-2]
                access_time = datetime.strptime(items[2], '[%Y-%m-%d %H:%M:%S]')
                yield (id, site_name, key, refer, username, access_time)

def process(audit_dict, filename, position, path, d, flag=None):
    for id, site_name, key, refer, username, access_time in read_file(filename):
        if id in audit_dict:
            if flag and not position.startswith('s'):
                if flag == 'uv':
                    uv_audit(audit_dict[id], key, username)
                else:
                    pv_audit(audit_dict[id], key, username, access_time)
            else:
                audit_both_pv_and_uv(audit_dict[id], key, username, access_time)
            if refer != 'None' and refer:
                refer_audit(audit_dict[id], REFER_KEY, refer)
        else:
            audit_dict[id] = {}
            audit_dict[id][key] = {}
            audit_dict[id][REFER_KEY]={}
            if flag and not position.startswith('s'):
                audit_dict[id][flag] = 1
            else:
                audit_dict[id]['uv'] = 1
                audit_dict[id]['pv'] = 1
            audit_dict[id]['advertiser'] = site_name
            audit_dict[id][key]['last_time'] = access_time
            audit_dict[id][key]['last_user'] = username
            if refer != 'None' and refer:
                audit_dict[id][REFER_KEY][refer] = 1
            if username != 'None':
                audit_dict[id][key].setdefault('username', []).append(username)

def pickle_data(audit_dict, path, position, flag, d):
    lastdata = {}
    result_dict = {}
    if flag:
        pick_name = '%s_%s.pk' % (position, flag)
    else:
        pick_name = '%s.pk' % position
    lastday = get_lastday(d)
    path_list = path.rsplit('/', 3)
    path_list[1] = str(lastday.year)
    path_list[2] = str(lastday.month)
    path_list[3] = str(lastday.day)
    lastday_path = os.path.join('/'.join(path_list), pick_name)
    if os.path.exists(lastday_path):
        lastdata = load_pickle_data(lastday_path)
    for id in audit_dict.iterkeys():
        result_dict[id] = {}
        if flag and not position.startswith('s'):
            result_dict[id][flag] = audit_dict[id][flag]
            add_lastday_data(result_dict, lastdata, id, flag)
        else:
            result_dict[id]['uv'] = audit_dict[id]['uv']
            add_lastday_data(result_dict, lastdata, id, 'uv')
            result_dict[id]['pv'] = audit_dict[id]['pv']
            add_lastday_data(result_dict, lastdata, id, 'pv')
        result_dict[id][REFER_KEY] = audit_dict[id][REFER_KEY]
        result_dict[id]['advertiser'] = audit_dict[id]['advertiser']
    if flag and not position.startswith('s'):
        key = 'sub_%s' % flag
        result_dict[key] = sum(result_dict[item][flag] for item in result_dict)
    else:
        total = sum(result_dict[item]['pv'] for item in result_dict)
        result_dict['sub_pv'] = total
        result_dict['sub_uv'] = total
    pick_file = os.path.join(path, pick_name)
    dump_data(pick_file, result_dict)

def add_lastday_data(result_dict, lastdata, id, flag):
    try:
        key = 'last-%s' % flag
        f = lastdata[id][flag]
    except KeyError:
        result_dict[id][key] = ''
    else:
        result_dict[id][key] = f

def audit_nature_area(d, page):
    blocks= NORMAL_BLOCKS[page]
    audit_dir = get_audit_data_dir(d)
    flag = None
    for area in blocks:
        audit_dict = {}
        filename = get_audit_filename(area)
        sub_path = os.path.join(audit_dir, page)
        log_path = os.path.join(sub_path, filename)
        process(audit_dict, log_path, area, sub_path, d)
        pickle_data(audit_dict, sub_path, area, flag, d)

def audit_spec_position_area(d, page):
    path = os.path.join(get_audit_data_dir(d), page)
    for flag in ['uv', 'pv']:
        patterns = get_position_pattern(path, page, flag)
        for pattern in patterns:
            for filename, position in get_position_file(pattern):
                audit_dict = {}
                process(audit_dict, filename, position, path, d, flag)
                pickle_data(audit_dict, path, position, flag, d)

def _audit_extra_area(d, flag, block, page):
    path = os.path.join(get_audit_data_dir(d), page)
    name, ext = os.path.splitext(settings.SITE_AUDIT_LOG_FILE)
    pattern = '%s_%s_%s*' % (name, flag, block)
    file_pattern = os.path.join(path, pattern)
    for filename, position in get_position_file(file_pattern):
        audit_dict = {}
        process(audit_dict, filename, position, path, d, flag)
        pickle_data(audit_dict, path, position, flag, d)

def audit_extra_area(d, page):
    page = 'city'
    #audit s area
    flag = 'pv'
    block = 's'
    _audit_extra_area(d, flag, block, page)
    #audit b area
   # flag = 'uv'
   # block = 'b'
   # _audit_extra_area(flag, block, page)

def _audit_sum(pick):
    with open(pickle_file, 'r') as f:
        data = pickle.load(pickle_file)
        result = sum(data[key]['pv'] for key in data)
    return result
    
def audit_nature_area_pv_sum(page):
    #normal area
    blocks= NORMAL_BLOCKS[page]
    audit_dir = get_audit_data_dir(d)
    pick_name = '%s.pk'
    sum_name ='sum_%s.pk'
    for area in blocks:
        audit_dir = os.path.join(audit_dir, page)
        pickle_file = os.path.join(audit_dir, pick_name % area)


def audit(d=None):
    d = d if d else get_lastday(datetime.now())
    for page in NORMAL_BLOCKS:
        audit_nature_area(d, page)
    for page in POSITION_BLOCKS:
        audit_spec_position_area(d, page)
    audit_extra_area(d, page)

class Command(BaseCommand):
    option_list = BaseCommand.option_list +(make_option('--date',\
                                            dest='date', default=None, help="Input a specific date, such as '2010-01-01'."),)
    def handle(self, **options):
        date = options.get('date', None)
        if date:
            date = date.split('-')
            if len(date) == 3:
                audit(datetime(int(date[0]), int(date[1]), int(date[2])))
            else:
                raise CommandError("You must input a date format like '2010-01-01'")
        else:
            audit()
