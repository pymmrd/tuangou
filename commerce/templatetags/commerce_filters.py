#! -*- coding:utf-8 -*-
from django.template import Library
register = Library()

@register.filter()
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try:
            return value * arg 
        except:
            return value
mul.is_safe = False

@register.filter()
def printf(value):
    return '%04d' % value
