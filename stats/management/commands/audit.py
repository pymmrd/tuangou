# -*- coding:utf-8 -*-
import os
import glob
import shlex
import subprocess
from django.conf import settings
from optparse import make_option
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand, CommandError
from tuangou.utils import get_log_path, dump_data, get_lastday, load_pickle_data
from tuangou.stats.utils.audit_site import get_audit_data_dir, \
    get_audit_filename

NORMAL_BLOCKS = {'city': ['a', 'b']}
POSITION_BLOCKS = {'city': ['c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']}
#PV_INTERVALS = 20 * 60
#REFER_KEY = 'refer'

def get_position_pattern(path, page, flag):
    blocks = POSITION_BLOCKS[page]
    name, ext = os.path.splitext(settings.SITE_AUDIT_LOG_FILE)
    for block in blocks:
        pattern = '%s_%s_%s*' % (name, flag, block)
        if os.path.exists(path):
            file_pattern = os.path.join(path, pattern)
            yield file_pattern, block

def get_position_file(pattern):
    file_list = glob.glob(pattern)
    for fi in file_list:
        filename = fi.rsplit('/', 1)[-1]
        filename, ext = os.path.splitext(filename)
        position = filename.split('_')[-1]
        yield (fi, position)

def pv_audit(f):
    click_cmd = "wc -l %s" % f
    args = shlex.split(click_cmd)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    result = p.stdout.read()
    try:
        number = int(result.split(' ')[0])
    except ValueError:
        number = 0
    return number

def audit_nature_area(d, page, audit_dict):
    flag = 'uv'
    blocks= NORMAL_BLOCKS[page]
    audit_dir = get_audit_data_dir(d)
    sub_path = os.path.join(audit_dir, page)
    for area in blocks:
        filename = get_audit_filename(area)
        log_path = os.path.join(sub_path, filename)
        if os.path.exists(log_path):
            pv = pv_audit(log_path)
            audit_dict[area] = {}
            audit_dict[area][flag] = pv

def audit_spec_position_area(d, page, audit_dict):
    flag = 'uv'
    path = os.path.join(get_audit_data_dir(d), page)
    patterns = get_position_pattern(path, page, flag)
    for pattern, block in patterns:
        for filename, position in get_position_file(pattern):
            pv = pv_audit(filename)
            if audit_dict.has_key(block):
                audit_dict[block].setdefault(flag, []).append(pv)
            else:
                audit_dict[block] = {}
                audit_dict[block].setdefault(flag, []).append(pv)
        audit_dict[block][flag] = sum(audit_dict[block][flag])

def audit(d=None):
    audit_dict = {}
    d = d if d else get_lastday(datetime.now())
    for page in NORMAL_BLOCKS:
        audit_nature_area(d, page, audit_dict)
    for page in POSITION_BLOCKS:
        audit_spec_position_area(d, page, audit_dict)
    pickle_data(audit_dict, d, page)

def pickle_data(audit_dict, d, page):
    pick_name = settings.PAGE_COUNTER_FILE % page
    path = os.path.join(get_audit_data_dir(d), page)
    pick_file = os.path.join(path, pick_name)
    dump_data(pick_file,audit_dict)

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
