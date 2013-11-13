# -*- coding:utf-8 -*-
import re
import urllib2
from lxml.html import fromstring
from tuangou.utils.cache import get_city_cache
from tuangou.guider.models import City, Shop, Deal_Shop_City_District, ReDeal, District

ADDR_REGX = re.compile(u'地址：(?P<addr>.+)')
TEL_REGX = re.compile(u'电话：(?P<tel>.+)')

def get_content(url):
    user_agents = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    headers = {'User-Agent':user_agents}
    req = urllib2.Request(url=url, headers=headers)
    content = urllib2.urlopen(req).read()
    return content

def _get_addr_district(addr, dis_list):
    pk = district = address =  None
    try:
        address = addr.group('addr')
    except AttributeError:
        address = addr
    for dis in dis_list:
        if address.find(dis[0]) != -1:
            district, pk = dis
            break
    return (address, district, pk)

def gen_record(pk, name, address, tel, city, dist, dist_pk):
    # gen shop 
    shop = None
    if name:
        shop, flag = Shop.objects.get_or_create(name=name, defaults={
        'telephone': tel,
        'address': address,
        })
    #gen district
    if dist_pk:
        district = District.objects.get(pk=dist_pk)
        deal = ReDeal.objects.get(pk=pk)
        deal.district.add(district)
    else:
        district = dist
    # gen relation
    if shop or district:
        old = Deal_Shop_City_District.objects.filter(deal_id=pk).delete()
        dscd = Deal_Shop_City_District()
        dscd.city = city
        dscd.deal_id = pk
        dscd.shop = shop
        dscd.district = district
        dscd.save()


path_dict = {
    'manzuo':"//div[@class='area']",
    'ftuan': "//div[@class='ProdBox clearfix']/div",
    'wowotuan': "//div[@class='adress']",
    'didatuan': "//div[@id='side-business']",
    'haotehui': "//div[@class='address']",
}
def common_spider(name, pk, slug, url):
    content = get_content(url)
    try:
        document = fromstring(content)
    except:
        raise
    else:
        city = get_city_cache(slug)
        fields = ('name', 'pk')
        dist_list = city.districts.values_list(*fields).filter(level=0, is_active=True)
        if dist_list:
            path = path_dict.get(name, None)
            blocks = document.xpath(path)
            for item in blocks:
                text = item.text_content().strip()
                for dis in dist_list:
                    if text.find(dis[0]) != -1: 
                        district, dist_pk = dis 
                        district = District.objects.get(pk=dist_pk)
                        deal = ReDeal.objects.get(pk=pk)
                        deal.district.add(district)
            
def lashou(pk, slug, url):
    content = get_content(url)
    try:
        document = fromstring(content)
    except:
        raise
    else:
        city = get_city_cache(slug)
        fields = ('name', 'pk')
        dist_list = city.districts.values_list(*fields).filter(level=0, is_active=True)
        if dist_list:
            try:
                block_c = document.xpath("//div[@class='r company']")[0]
            except IndexError:
                block_c = document.xpath("//div[@class='trip_content']/div[7]")
                if block_c:
                    b_detail = block_c[0]
                    address=telephone = ''
                    district=dist_pk = None
                    for item in b_detail.iterchildren():
                        text = item.text.strip()
                        addr = ADDR_REGX.match(text)
                        tel = TEL_REGX.match(text)
                        if addr is not None:
                            address, district, dist_pk = _get_addr_district(addr, dist_list)
                        elif tel is not None:
                            telephone = tel.group('tel')
                        else:
                            name = text
                        gen_record(pk, name, address, telephone, city, district, dist_pk)
            else:
                b_name = block_c.find('h3')
                try:
                    name = b_name.text.strip()
                except AttributeError:
                    name = None
                else:
                    b_detail = block_c.xpath(".//ul/li")
                    shop = name
                    for li in b_detail:
                        address=telephone = ''
                        district=dist_pk = None
                        for item in li.iterchildren():
                            text = item.text.strip()
                            addr = ADDR_REGX.match(text)
                            tel = TEL_REGX.match(text)
                            if item.tag == 'b':
                                suffix = text
                                shop = '%s(%s)' % (name, suffix) 
                            elif addr is not None:
                                address, district, dist_pk = _get_addr_district(addr, dist_list)
                            elif tel is not None:
                                telephone = tel.group('tel')
                        gen_record(pk, shop, address, telephone, city, district, dist_pk) 
