# -*- coding:utf-8 -*-

import re
import os
import operator
from datetime import datetime, timedelta

regx = re.compile(r'.+MAC=(?P<mac>.+)&Ver=.+')
static_regx = re.compile('.+/static/.+')
commerce_regx = re.compile('.+/commerce/.+')

def get_log_file(lastday):
    log_file = '/var/log/httpd/tuangou_access_%s_%s_%s.log'
    result = 'result_%s_%s_%s.txt'
    year = lastday.strftime('%Y')
    month = lastday.strftime('%m')
    day = lastday.strftime('%d')
    log_file = log_file % (year, month, day)
    result = result % (year, month, day)
    return log_file, result

def process(d):
    log_file ,result = get_log_file(d)
    adict = {}
    with open(log_file, 'r') as f:
        for line in f:
            static = static_regx.match(line)
            commerce = commerce_regx.match(line)
            if static is None or commerce is None:
                match = regx.match(line)
                if match is not None:
                    mac = match.group('mac')
                    if mac not in  adict:
                        adict[mac] = 1
                    else:
                        adict[mac] += 1
    items = adict.iteritems()
    sorted_items = sorted(items, key=operator.itemgetter(1))
    for index, (key, value) in enumerate(sorted_items):
        if value ==2:
            break
    log_path = '/home/php_audit/laidiantuan/action'
    log_file = os.path.join(log_path, result)
    with open(log_file, 'w') as f:
        for key, value in sorted_items[index:]:
            f.write('%s%s' % (key, os.linesep))
        
if __name__ == '__main__':
    import sys
    args = sys.argv[1]
    d = datetime.strptime(args, '%Y-%m-%d')
    if d:
        lastday = d
    else:
        lastday = datetime.today() - timedelta(days=1)
    process(lastday)
