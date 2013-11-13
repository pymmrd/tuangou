# -*- coding:utf-8 -*-
import re
REGX = re.compile('http://(?P<domain>.+?)/.+')
SEARCH_ENGINE = {'www.baidu.com':'baidu', 'www.google.cn':'google', 'www.yahoo.com.cn':'yahoo', 'www.sogou.com':'sogou', 'www.sina.com':'sina', 'so.163.com':'wangyi', 'www.laidiantuan.com': ''}

def parse(link):
    domain = REGX.match(link)
    name = ''
    if domain is not None:
        domain_name  = domain.group('domain')
        try:
            name = SEARCH_ENGINE[domain_name]
        except KeyError:
            name = ''
    return name


