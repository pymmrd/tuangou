# -*- coding: utf-8 -*-
from django.template import Library
from django.template.defaultfilters import slice_
from tuangou.utils import smart_unicode

register = Library()

@register.filter()
def safe_slice(value, arg):
    """enforce value to unicode"""
    value = smart_unicode(value)
    return slice_(value, arg)

@register.filter()
def safe_slice_dot(value, arg):
    """enforce value to unicode"""
    value = smart_unicode(value)
    result = slice_(value, arg)
    return len(result) < len(value) and (result + u'...') or result

@register.filter()
def int_type(value):
    return int(value)
