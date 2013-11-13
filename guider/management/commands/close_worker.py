# -*- coding:utf-8 -*-
import os
import subprocess
from celery.task.control import inspect, broadcast
from django.core.management.base import BaseCommand, NoArgsCommand

#INDEX_UPDATE = 'python2.6 /var/www/tuangou/manage.py update_index'
INIT_DEAL  = 'python2.6 /var/www/tuangou/manage.py init_deal'
SOLID_CITY = 'python2.6 /var/www/tuangou/manage.py solid_page_city'
SELLER_CHART = 'python2.6 /var/www/tuangou/manage.py solid_chart'

os.environ['PYTHON_EGG_CACHE'] = '%s/PYTHON_EGG_CACHE' % '/tmp'
CLOSE_FLAG = 'close_flag.txt'

def watcher():
    #try:
    #    f = open(CLOSE_FLAG, 'r')
    #except IOError:
        #i = inspect()
        #workers = i.active()
        #if not all(workers.itervalues()):
        #    broadcast('shutdown')
        #    with open(CLOSE_FLAG, 'w') as f:
        #        f.write('%s%s' % ('true', os.linesep))
    init = subprocess.Popen(INIT_DEAL, shell=True)
    init.wait()
    op = subprocess.Popen(SOLID_CITY, shell=True)
    op.wait()
    #sp = subprocess.Popen(INDEX_UPDATE, shell=True)
    #sp.wait()
    pp = subprocess.Popen(SELLER_CHART, shell=True)
    pp.wait()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        watcher()
