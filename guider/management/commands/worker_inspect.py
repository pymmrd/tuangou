# -*- coding:utf-8 -*-
import os
import subprocess
from celery.task.control import inspect, broadcast
from django.core.management.base import BaseCommand, NoArgsCommand

os.environ['PYTHON_EGG_CACHE'] = '%s/PYTHON_EGG_CACHE' % '/tmp'
RECOMBINE_CMD = 'python2.6 /var/www/tuangou/manage.py custom'
CLASSIFY = 'python2.6 /var/www/tuangou/manage.py classify'
DISTRICT = 'python2.6 /var/www/tuangou/manage.py spider_dist'
RUN_FLAG_FILE = 'custom_flag.txt'

def watcher():
    try:
        f = open(RUN_FLAG_FILE, 'r')
    except IOError:
        i = inspect()
        workers = i.active()
        if not all(workers.itervalues()):
            with open(RUN_FLAG_FILE, 'w') as f:
                f.write('%s%s' % ('true', os.linesep))
            p = subprocess.Popen(RECOMBINE_CMD, shell=True)
            p.wait()
            cp = subprocess.Popen(CLASSIFY, shell=True)
            cp.wait()
            dp = subprocess.Popen(DISTRICT, shell=True)
            dp.wait()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        watcher()
