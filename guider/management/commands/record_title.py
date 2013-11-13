# -*- coding:utf-8 -*-
from tuangou.guider.models import  *
from django.core.management.base import NoArgsCommand, CommandError

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
            for deal in ReDeal.objects.values_list('title', flat=True):
                print deal
