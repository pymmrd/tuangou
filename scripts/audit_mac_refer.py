# -*- coding: utf-8 -*-
import re
import os
import marshal
import operator
import optparse
from datetime import datetime, timedelta

INCERPT_NUM = 100
regx = re.compile(r'.+MAC=(?P<mac>.+)&Ver=.+')
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), '%s/%s' %('log', 'refer'))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
REFER_FILE = 'refer_%s_%s_%s.mar'
STATIC_REGX = re.compile('.+/static/.+')
UNINSTALL_REGX = re.compile('.+/uninstall.+')
COMMERCE_REGX = re.compile('.+/commerce.+')
REFER_REGX = re.compile('http://.+?/')
PHP_REGX = re.compile('.+/phpmyadmin.+')
DOMAIN = 'http://www.laidiantuan.com/'

def get_log_file(lastday):
    log_file = '/var/log/httpd/tuangou_access_%s_%s_%s.log'
    result = 'result_%s_%s_%s.txt'
    year = lastday.strftime('%Y')
    month = lastday.strftime('%m')
    day = lastday.strftime('%d')
    log_file = log_file % (year, month, day)
    result = result % (year, month, day)
    refer_file = REFER_FILE % ( year, month, day)
    return log_file, result, refer_file

def audit_mac(line, mac_dict):
    match = regx.match(line)
    if match is not None:
        mac = match.group('mac')
        mac_dict[mac] = mac_dict.get(mac, 0) + 1

def gen_mac_result(mac_dict, result):
    sorted_items = sorted(mac_dict.iteritems(), key=operator.itemgetter(1))
    for index, (key, value) in enumerate(sorted_items):
        if value ==2:
            break
    log_path = '/home/php_audit/laidiantuan/action'
    log_file = os.path.join(log_path, result)
    with open(log_file, 'w') as f:
        for key, value in sorted_items[index:]:
            f.write('%s%s' % (key, os.linesep))
    
def get_lastday(d=None):
    if d:
        lastday = d
    else:
        lastday = datetime.now() - timedelta(days=1)
    return lastday

def dump_data(result, pick_file):
    with open(pick_file, 'w') as f:
        marshal.dump(result, f)

def audit_refer(line, audit_dict):
    refer = line.split('"')[3].strip()
    search = REFER_REGX.search(refer)
    if search is not None: 
        refer = search.group()
        if refer != DOMAIN :
            audit_dict[refer] = audit_dict.get(refer, 0) + 1
    else:
        if refer == 'http://www.laidiantuan.com' or refer == '-':
            pass
        else:
            audit_dict[refer] = audit_dict.get(refer, 0) + 1

def gen_refer_result(audit_dict, refer_file):
    audit_list = sorted(audit_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
    length = len(audit_list)
    index = INCERPT if length > INCERPT_NUM else length
    audit_list = audit_list[:index-1]
    pick_file  = os.path.join(LOG_DIR, refer_file)
    dump_data(audit_list, pick_file)

def audit(d):
    audit_dict = {}
    mac_dict = {}
    lastday = get_lastday(d)
    log_file ,result , refer_file= get_log_file(lastday)
    with open(log_file, 'r') as f:
        for line in f:
            static = STATIC_REGX.match(line)
            commerce = COMMERCE_REGX.match(line)
            uninstall = UNINSTALL_REGX.match(line)
            php = PHP_REGX.match(line)
            if static is not None or commerce is not None or uninstall is not None or php is not None:
                continue
            audit_refer(line, audit_dict)
            #audit_mac(line, mac_dict)
    #gen_mac_result(mac_dict, result)
    gen_refer_result(audit_dict, refer_file)

if __name__ == "__main__":
    p = optparse.OptionParser()
    p.add_option('-d', '--date', action='store', dest='date')
    opt, args = p.parse_args()
    try:
        date = datetime.strptime(opt.date, '%Y-%m-%d')
    except:
        date = None
    audit(date)
