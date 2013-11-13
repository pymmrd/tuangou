# -*- coding:utf-8 -*-
import os
import subprocess
from celery.task.control import inspect, broadcast
from django.core.management.base import BaseCommand, NoArgsCommand

RECOMBINE_CMD = 'python2.6 /var/www/tuangou/manage.py custom'
INDEX_UPDATE = 'python2.6 /var/www/tuangou/manage.py update_index'
RUN_FLAG_FILE = 'custom_flag.txt'

def watcher():
    try:
        f = open(RUN_FLAG_FILE, 'r')
    except IOError:
        with open(RUN_FLAG_FILE, 'w') as f:
            i = inspect()
            print >>f, '1'
            workers = i.active()
            print >>f, '2'
            if not all(workers.itervalues()):
                pirnt >>f, '3'
                broadcast('shutdown')
                f.write('%s%s' % ('true', os.linesep))

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        watcher()
