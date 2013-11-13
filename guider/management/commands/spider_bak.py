# -*- coding:utf-8 -*-

import sys
import traceback
import threading
import multiprocessing
from optparse import make_option
from django.conf import settings
from tuangou.guider.models import Website
from tuangou.utils import app_error_log
from django.core.management.base import BaseCommand, CommandError
from base import *

NORMAL = 1
ENHANCE = 2
OTHER = 3
NONE = 0

APINAME_OF_SITE ={u'糯米': [
    {'yinchuan':u'银川'}, {'changchun':u'长春'}, {'luoyang':u'洛阳'}, {'shantou':u'汕头'}, {'weihai':u'威海'}, {'wuhu':u'芜湖'}, {'kunming':u'昆明'}, {'xiangtan': u'湘潭'}, {'shenzhen':u'深圳'}, {'haikou':u'海口'}, 
    {'nanning':u'南宁'}, {'chongqing':u'重庆'}, {'taizhou':u'台州'}, {'zhuzhou':u'株州'}, {'shijiazhuang':u'石家庄'}, {'lianyungang':u'连云港'}, {'taizhoux':u'泰州'}, {'xian':u'西安'}, {'eerduosi':u'鄂尔多斯'}, {'dongying':u'东营'},
    {'xining':u'西宁'}, {'handan':u'邯郸'}, {'bengbu':u'蚌埠'}, {'huzhou':u'湖州'}, {'tangshan':u'唐山'}, {'xianyang':u'襄阳'}, {'xiamen':u'厦门'}, {'dezhou':u'德州'}, {'jilin':u'吉林'}, {'jiaxing':u'嘉兴'}, 
    {'lanzhou':u'兰州'}, {'kaifeng':u'开封'}, {'dongguan':u'东莞'},{'jinhua':u'金华'}, {'guilin':u'桂林'}, {'guiyang':u'贵阳'}, {'zhongshan':u'中山'},{'zhengzhou':u'郑州'}, {'changzhou':u'常州'}, {'foshan':u'佛山'},
    {'huaian':u'淮安'}, {'anshan':u'鞍山'}, {'taian':u'泰安'}, {'hegang':u'鹤岗'}, {'maoming':u'茂名'}, {'baoji':u'宝鸡'}, {'yancheng':u'盐城'},{'haerbin':u'哈尔滨'}, {'xuzhou':u'徐州'}, {'zaozhuang':u'枣庄'},
    {'changsha':u'长沙'}, {'wenzhou':u'温州'}, {'shenyang':u'沈阳'}, {'zhoushan':u'舟山'}, {'zhanjiang':u'湛江'}, {'xingtai':u'邢台'}, {'chengde':u'承德'}, {'taiyuan':u'太原'}, {'weifang':u'潍坊'},{'jinan':u'济南'},
    {'ningbo':u'宁波'},{'baoding':u'保定'},{'zhenjiang':u'镇江'},{'zhangzhou':u'漳州'}, {'fuzhou':u'福州'}, {'hangzhou':u'杭州'}, {'panjin':u'盘锦'},{'nanyang':u'南阳'}, {'xuchang':u'许昌'}, {'qinhuangdao':u'秦皇岛'},
    {'liuzhou':u'柳州'}, {'pingdingshan':u'平顶山'}, {'liaocheng':u'聊城'}, {'huangshi':u'黄石'}, {'tianjin':u'天津'}, {'jiangmen':u'江门'},{'cangzhou':u'沧州'}, {'wuxi':u'无锡'}, {'jining':u'济宁'}, {'rizhao':u'日照'},
    {'yangzhou':u'扬州'}, {'binzhou':u'滨州'}, {'qiqihar':u'齐齐哈尔'},{'nanjing':u'南京'}, {'suzhou':u'苏州'}, {'chengdu':u'成都'}, {'hohhot':u'呼和浩特'}, {'wuhan':u'武汉'}, {'yichang':u'宜昌'}, {'nanchang':u'南昌'},
    {'shanghai':u'上海'}, {'nantong':u'南通'}, {'baotou':u'包头'}, {'yantai':u'烟台'}, {'hefei':u'合肥'}, {'zibo':u'淄博'}, {'quanzhou':u'泉州'},{ 'yueyang':u'岳阳'}, {'langfang':u'廊坊'}, {'sanya':u'三亚'},
    {'shaoxing':u'绍兴'}, {'putian':u'莆田'}, {'huizhou':u'徽州'}, {'linyi':u'临沂'}, {'dalian':u'大连'}, {'beijing':u'北京'}, {'daqing':u'大庆'}, {'guangzhou':u'广州'}, {'qingdao':u'青岛'},
    ]} 

class SpiderThread(threading.Thread):
    def __init__(self, site, spider, workerq):
        self.site = site
        self.spider = spider
        self.workerq = workerq
        super(self.__class__, self).__init__()

    def run(self):
        while True:
            try:
                item = self.workerq.get_nowait()
                self.spider.deal_url = self.site.deal_api % item.api_name 
                self.spider.parse_deals_api(self.site)
            except Queue.Empty:
                break

def gen_city_and_api_name(site):
    city_list = None
    if not site.city_api:
        try:
            city_list = APINAME_OF_SITE[site.name]
        except KeyError:
            pass
    if site.city_crawl_type == NONE or site.city_crawl_type == NORMAL:
        spider = CitySpider(api_addr=site.city_api, api_list=city_list)
    elif site.city_crawl_type == ENHANCE:
        spider = EnhanceCitySpider(api_addr=site.city_api, api_list=city_list)
    #TODO INIT
    spider.parse_city(site)

def gen_deal_record(site):
    if site.deal_crawl_type == NORMAL:
        spider = DealSpider(deal_url=site.deal_api)
    elif site.deal_crawl_type == ENHANCE:
        spider = EnhanceDealSpider(deal_url=site.deal_api)
    if not site.api_tags_active:
        spider.parse_deals_api(site)
    else:
        apis = site.cityapi.all()
        for api in apis: 
            spider.deal_url = site.deal_api % api.api_name
        spider.parse_deals_api(site)
            
def crawl(worker):
    #sites = Website.actives.all()[6:]
    site = Website.objects.get(pk=73)
    #for site in sites:
    gen_deal_record(site)
    #gen_city_and_api_name(site)

"""
    def crawl(worker):
        from django.db import connection
        connection.close()
        p = multiprocessing.Pool(worker)
        p.map(spiderman, Website.actives.all())
        p.close()
        p.join()
"""    
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--worker', dest='worker', default=2),
    )

    def handle(self, **options):
        worker = int(options.get('worker', 2))
        crawl(worker)
