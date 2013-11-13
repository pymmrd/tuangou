#-*- coding:utf-8 -*-
import re
import os
import sys
import time
import urllib2
import string
import socket
import traceback
from PIL import Image
from random import choice
from itertools import izip
from StringIO import StringIO
from contextlib import closing
from datetime import datetime
from django.conf import settings
from django.db import IntegrityError
from decimal import Decimal, getcontext
#from xml.etree import cElementTree as ET
from lxml import etree as ET
from django.utils.hashcompat import md5_constructor
from tuangou.utils import app_error_log, get_log_file
from tuangou.guider.models import City, Shop, Deal, District, CityAPIName, Deal_Shop_City_District 

socket.setdefaulttimeout(20)

PRICE_FILTER = [',', u'折', u'￥', u'元', '-']
SEPERATOR = string.punctuation + u'，；'
TITLE_LIST = ['nuomi', ]

class SpiderBase(object):
    def _get_content(self, url):
        with closing(urllib2.urlopen(url)) as page:
            return page.read()

    def tryAgain(self, url, flag=None, retries=0):
        while True:
            if retries > 4: 
                if flag:
                    return ''
                else:
                    return '<null></null>'
            try:
                time.sleep(1)
                content =self._get_content(url)
                if not flag:
                    content = content
            except (urllib2.URLError, SyntaxError, ValueError, socket.error, socket.timeout):
                retries+=1
                content = self.tryAgain(url, flag, retries)
            return content

    def create_etree(self, url):
        content = self.get_content(url)
        try:
            etree = ET.fromstring(content)
        except SyntaxError:
            etree = ET.fromstring('<null></null>')
        return etree
            
    def get_content(self, url, flag=None):
        user_agents = [
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Opera/9.25 (Windows NT 5.1; U; en)',
           "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.17) Gecko/20110422 Ubuntu/10.04 (lucid) Firefox/3.6.17"
        ]
        headers = {'User-Agent':choice(user_agents)}
        req = urllib2.Request(url=url, headers=headers)
        try:
            content = self._get_content(req)
        except urllib2.HTTPError, e:
            if e.code == 503:
                time.sleep(1)
                content = self.tryAgain(req, flag)
            if e.code == 404:
                if not flag:
                    content = '<null></null>'
                else:
                    content = ''
        except (urllib2.URLError, socket.timeout, ValueError, socket.error):
            time.sleep(1)
            content = self.tryAgain(req, flag)
        return content

    def get_text(self, elem, tag):
        return elem.find(tag).text

    def get_elems(self, url):
        etree = self.create_etree(url)
        child_tree = etree.getchildren()
        childs = (child for child in child_tree if child.getchildren())
        return childs

class CitySpider(SpiderBase):
    def __init__(self, api_addr, api_list=None):
        self.api_addr = api_addr
        self.api_list = api_list

    def get_text(self, elem, tag):
        return list(elem.getiterator(tag))[0].text.strip()

    def create_related(self, site, name, api_name):
        city, flag = City.objects.get_or_create(name=name)
        api, flag = CityAPIName.objects.get_or_create(api_name=api_name)
        site.opened_city.add(city)
        site.cityapi.add(api)
        site.save()

    def get_field_map(self, site):
        field_map = dict(izip(settings.CITY_TUPLE, site.city_api_tags.split(',')))
        return field_map

    def _parse_city(self, site, elems):
        field_map = self.get_field_map(site)
        for elem in elems:
            api_name = self.get_text(elem, field_map[settings.CITY_API_NAME])
            name = self.get_text(elem, field_map[settings.CITY_NAME])
            self.create_related(site, name, api_name)

    def parse_city(self, site):
        if site.city_api:
            elems = self.get_elems(self.api_addr)
            self._parse_city(site, elems)

        if isinstance(self.api_list, list) or isinstance(self.api_list, tuple):
            for name in self.api_list:
                api_name, c = name.items()[0]
                self.create_related(site, c, api_name)

class DealSpider(SpiderBase):
    def __init__(self, deal_url):
        self.deal_url = deal_url

    def get_text(self, elem, field_map, node):
        try:
            tag = field_map[node]
        except KeyError:
            result = ''
        else:
            items = list(elem.getiterator(tag))
            len_items = len(items)
            if len_items == 1 or node == 'description':
                try:
                    text = items[0].text.strip()
                except (IndexError, AttributeError):
                    result = ''
                else:
                    result = text if text else ''
            elif len_items > 1:
                result = [item.text.strip() for item in items if item.text]
            else:
                result = ''
        return result

    def get_field_map(self, site):
        deal_map = {}
        fields = site.deal_map.all()
        for field in fields:
            deal_map[field.origin_field] = field.node
        return deal_map

    def filter_price(self, elem, field_map, tag, origin_price=None, price=None):
        scalar = self.get_text(elem, field_map, tag)
        if not scalar  and tag == settings.DEAL_DISCOUNT:
            if not price:
                return Decimal('0.0')
            else:
                getcontext().prec=3
                scalar  = origin_price * 10 / price
        else:
            for mark in PRICE_FILTER:
                scalar = scalar.replace(mark, '')
        try:
            return Decimal(scalar)
        except:
            return Decimal('0.0')

    def save_image(self, image, image_name, path):
        image_dirs = "%s/%s" % (settings.MEDIA_ROOT, path)
        if not os.path.exists(image_dirs):
            os.makedirs(image_dirs)
        image_path = os.path.join(image_dirs, image_name)
        if os.path.exists(image_path):
            name, ext = os.path.splitext(image_name)
            image_name = name + str(time.time())+ext
            image_path = os.path.join(image_dirs, image_name)
        try:
            image.save(image_path, quality=100)
        except TypeError:
            image_name = image_name +'.'+ image.format
            image_paht = os.path.join(image_dirs, image_name)
            image.save(image_name, quality=100)
        except  KeyError:
            image.save(image_path, 'JPEG', quality=100)
        except IOError:
            image.mode = 'RGB'
            image.save(image_path, quality=100)
        return "%s/%s" % (path, image_name)

    def gen_normal_image(self, image):
        i_width = image.size[0]
        width = settings.IMAGE_WIDTH 
        if i_width > width:
            ratio = float(width)/ i_width
            height = int(image.size[1] * ratio)
            image = image.resize((width, height), Image.BILINEAR)
        return image

    def gen_thumbnail_image(self, image):
        image.thumbnail((settings.THUMB_WIDTH, settings.THUMB_HEIGHT)) 
        return image

    def get_image(self, image_url, site):
        regx = re.compile(r'[?&=]')
        now = datetime.now()
        image_name = image_url.rsplit('/', 1)[-1]
        image_name = regx.sub('', image_name)
        print image_name
        content = StringIO(self.get_content(image_url, flag='image'))
        try:
            image = Image.open(content)
        except IOError:
            return ('', '')
        else:
            image_sub_path = "%s/%s/%s/%s" % (now.year, now.strftime('%m'), now.strftime('%d'), site.slug)
            normal_image_path = os.path.join(image_sub_path, 'normal')
            im = self.gen_normal_image(image)
            normal_path = self.save_image(im, image_name, normal_image_path)
            thumbnail = os.path.join(image_sub_path, 'thumbnail')
            im = self.gen_thumbnail_image(image)
            thumb_path = self.save_image(im, image_name, thumbnail)
            return (normal_path, thumb_path)

    def convert_date(self, s, site):
        if site.date_fmt:
            return datetime.strptime(s, site.date_fmt)
        else:
            return datetime.fromtimestamp(int(s))

    def gen_district_from_title(self, city, deal, title):
        regx = re.compile(u'【(?P<district>.+?)】.+')
        match = regx.match(title)
        if match is not None:
            dist = match.group('district')
            print dist
            #district, flag = District.objects.get_or_create(name=dist, city=city)
            #deal.district.add(district)

    def _gen_district(self, text, deal, city):
        punct = string.punctuation
        districts = []
        if text:
            items = re.split(r'[\s%s‘]' % punct, text) 
            items = [item for item in items if item]
            for item in items:
                district, flag = District.objects.get_or_create(name=item, city=city)
                deal.district.add(district)
                districts.append(district)
        return districts 

    def _gen_shop(self, elem, field_map, city, deal):
        district = self.get_text(elem, field_map, settings.DEAL_DIS)
        shop = self.get_text(elem, field_map, settings.DEAL_SHOP)

        def __gen_shop(name, telephone, address, longitude, latitude, url, district, deal, city):
            shop, flag = Shop.objects.get_or_create(name=name, defaults={
            'telephone': telephone,
            'address': address,
            'longitude': longitude,
            'latitude': latitude,
            'url': url,
            })
            districts = self._gen_district(district, deal, city) 
            for district in districts:
                Deal_Shop_City_District.objects.get_or_create(deal_id=deal.id, shop=shop, city=city, district=district)

        if shop:
            url = self.get_text(elem, field_map, settings.SHOP_URL)
            telephone = self.get_text(elem, field_map, settings.SHOP_TEL)
            address = self.get_text(elem, field_map, settings.SHOP_ADDR)
            longitude = self.get_text(elem, field_map, settings.SHOP_LNG)
            latitude = self.get_text(elem, field_map, settings.SHOP_LAT)
            if isinstance(shop, list):
                shop_num = len(shop)
                if isinstance(url, basestring):
                    url = [url] * shop_num
                if isinstance(telephone, basestring):
                    telephone = [telephone] * shop_num
                if isinstance(address, basestring):
                    address = [address] * shop_num
                if isinstance(longitude, basestring):
                    longitude = [longitude] * shop_num
                if isinstance(latitude, basestring):
                    latitude = [latitude] * shop_num
                if isinstance(district, basestring):
                    district = [district] * shop_num
                items = izip(shop, telephone, address, longitude, latitude, url, district) 
                for item in items:
                    __gen_shop(item[0], item[1], item[2], item[3], item[4], item[5], item[-1], deal, city)
            if isinstance(shop, basestring):
                __gen_shop(shop, telephone, address, longitude, latitude, url, district, deal, city)
        else:
            shop = None
            districts = self._gen_district(district, deal, city)
            #if districts:
                #for district in districts:
                    #Deal_Shop_City_District.objects.get_or_create(deal_id=deal.id, shop=shop, city=city, district=district)
            #else:
                #district=None
                #Deal_Shop_City_District.objects.get_or_create(deal_id=deal.id, shop=shop, city=city, district=district)
        
    def _gen_city(self, elem, field_map):
        text = self.get_text(elem, field_map, settings.DEAL_DIVISION)
        if text and not text.startswith(u'全国'):
            texts = re.split(r'[\s%s]' % SEPERATOR, text) 
            items = [item.strip() for item in texts if item]
            divisions = [City.objects.get_or_create(name=item)[0] for item in items]
        else:
            division, flag= City.objects.get_or_create(name=u'全国')
            divisions = [division]
        return divisions

    def _gen_deal(self, website, elem, field_map, cities):
        deal = None
        title = self.get_text(elem, field_map, settings.DEAL_TITLE)
        city =  None if len(cities)>= 2 else cities[0]
        if website.slug in TITLE_LIST:
           self.gen_district_from_title(city, deal, title)
        try:
            bought = int(self.get_text(elem, field_map, settings.DEAL_BOUGHT))
        except ValueError:
            bought = 0
        deal_url = self.get_text(elem, field_map, settings.DEAL_URL)
        start_date = self.convert_date(self.get_text(elem, field_map, settings.DEAL_START_DATE), website)
        end_date = self.convert_date(self.get_text(elem, field_map, settings.DEAL_END_DATE), website)
        origin_price = self.filter_price(elem, field_map, settings.DEAL_ORIGIN_PRICE)
        price = self.filter_price(elem, field_map, settings.DEAL_PRICE)
        print "price--->", price
        discount = self.filter_price(elem, field_map, settings.DEAL_DISCOUNT, origin_price, price)
        description = self.get_text(elem, field_map, settings.DEAL_DSR)
        image_url = self.get_text(elem, field_map, settings.DEAL_IMAGE)
        image, thumbnail = self.get_image(image_url, website)
        md5sum = md5_constructor('%s%s%s%s' % (title, website.name, start_date, end_date)).hexdigest()
        deal = None
        image = None
        if image:
            pass
            """
            try:
                deal = Deal.objects.get(md5sum=md5sum)
            except Deal.DoesNotExist:
                deal = Deal()
                deal.md5sum = md5sum
                deal.title = title
                deal.website = website
                deal.start_date = start_date
                deal.end_date = end_date
                deal.deal_url = deal_url
                deal.price = price
                deal.bought = bought
                deal.discount = discount
                deal.origin_price = origin_price
                deal.description = description
                deal.thumbnail = thumbnail
                deal.image = image
                deal.save()
                for city in cities:
                    deal.division.add(city)
                #from guider.tasks import classify
                #classify.apply_async(args=(deal.pk, ))
                city =  None if len(cities)>= 2 else cities[0]
                if website.slug in TITLE_LIST:
                   self.gen_district_from_title(city, deal, title)
                else:
                    self._gen_shop(elem, field_map, city, deal)
                self._gen_shop(elem, field_map, city, deal)
            """
        return deal

    def parse_deals_api(self, site):
        field_map = self.get_field_map(site)
        elems = self.get_elems(self.deal_url)
        print self.deal_url
        for elem in elems:
            try:
                cities = self._gen_city(elem, field_map) 
                for city in cities:
                    site.opened_city.add(city)
                deal = self._gen_deal(site, elem, field_map, cities)
            except: 
                with open(get_log_file(settings.SPIDER_ERROR_LOG), 'a') as f:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    f.write("%s\t%s%s" %(site.name.encode('utf-8'), self.deal_url.encode('utf-8'),  os.linesep))
                    f.write('[%s]' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    traceback.print_exception(exc_type,
                                              exc_value,
                                              exc_tb, 
                                              limit=7,
                                              file=f)
                    f.write('%s' % os.linesep)
                    f.flush()

class EnhanceCitySpider(CitySpider):
    def __init__(self, api_addr, api_list):
        super(self.__class__, self).__init__(api_addr, api_list)

    def get_elems(self, url):
        etree = self.create_etree(url)
        first_node = (sub for sub in etree.getchildren())
        childs = (child for node in first_node for  child in node.getchildren())
        return childs

class EnhanceDealSpider(DealSpider):
    def __init__(self, deal_url, *args, **kwargs):
        super(self.__class__, self).__init__(deal_url)

    def get_elems(self, url):
        etree = self.create_etree(url)
        first_node = (sub for sub in etree.getchildren())
        childs = (child for node in first_node  for  child in node.getchildren())
        return childs
