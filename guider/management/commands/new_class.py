# -*- coding;Utf-8 -*-

import operator
from collections import defaultdict
from tuangou.guider.models import  MatchWord, Category, ReDeal
from django.core.management.base import NoArgsCommand, CommandError

def get_deals():
    for deal in ReDeal.nonexpires.filter(category=None):
        yield deal

def classify_process(deal):
    match_dict = defaultdict(int)
    for cat in Category.objects.active().exclude(parent=None):
        for keyword in cat.matchwords.all():
            if deal.title.find(keyword.word) != -1:
                match_dict[cat]  += 1
    match_items = match_dict.items()
    sorted_items = sorted(match_items, key=operator.itemgetter(1), reverse=True)
    try:
        match_cat = sorted_items[0][0]
    except IndexError:
        pass
    else:
        deal.category = match_cat
        deal.save()

def classify():
    for deal in get_deals():
        classify_process(deal)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        classify()
