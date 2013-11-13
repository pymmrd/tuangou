#-*- coding:utf-8 -*-
# Django settings for tuangou project.
from celery.schedules import crontab
import djcelery
djcelery.setup_loader()

import os
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__).encode('utf-8')).replace('\\', '/')

#DEBUG = True
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
MASTER = 'default'
SLAVE = 'slave'

DATABASES = { 
    MASTER: {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'tuangou',                      # Or path to database file if using sqlite3.
        #'USER': 'admin',                      # Not used with sqlite3.
        'USER': 'zg163',                      # Not used with sqlite3.
        #'PASSWORD': '1234.asd',                  # Not used with sqlite3.
        'PASSWORD': 'admin4u',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },  
    #MASTER: {
    #    'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #    'NAME': 'tuangou',                      # Or path to database file if using sqlite3.
    #    'USER': 'zg163',                      # Not used with sqlite3.
    #    'PASSWORD': 'admin4u',                  # Not used with sqlite3.
    #    'HOST': '119.161.216.83',                      # Set to empty string for localhost. Not used with sqlite3.
    #    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    #}   
}
#DATABASE_ROUTERS = ['db_routers.RW_routers.MasterSlaveRouter', ]
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Asia/Hong_Kong'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-cn'
DEFAULT_CHARSET = 'utf-8'
DEFAULT_CITY = 'beijing'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join('/home', 'static')
#MEDIA_ROOT = os.path.join(CURRENT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://static.laidiantuan.com/static/'
#MEDIA_URL = 'http://119.161.216.83:8080/static/'
EXTRA_MEDIA_URL = '/extra/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/' 
# Make this unique, and don't share it with anybody.
SECRET_KEY = '&4j-#u_b(77x)0o18tow!#9dj^av!-z6y!cy0ufv4r@0ha80)m'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tuangou.IPLocationMiddleware.Location',
)

ROOT_URLCONF = 'tuangou.urls'
TEMPLATE_CONTEXT_PROCESSORS = ( 
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'tuangou.guider.context_processor.guider_context',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CURRENT_PATH, 'templates'),
    '/var/www',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'guider',
    'utils',
    #'haystack',
    'wishlist',
    'solid',
    'search',
    'stats',
    'accounts',
    'commerce',
    'union',
)
INSTALLED_APPS += ('djcelery', )
IMAGE_WIDTH = 220
IMAGE_HEIGHT = 140
CITY_NAME = 'name'
DEAL_TITLE = 'title'
DEAL_IMAGE = 'image'
DEAL_PRICE  = 'price'
DEAL_SHOP = 'shop'
DEAL_DSR = 'description'
DEAL_DIS = 'district'
DEAL_URL = 'deal_url'
DEAL_BOUGHT = 'bought'
DEAL_DISCOUNT = 'discount'
CITY_API_NAME = 'api_name'
DEAL_DIVISION = 'division'
DEAL_END_DATE = 'end_date'
DEAL_START_DATE = 'start_date'
SHOP_URL = 'shop_url'
SHOP_ADDR = 'address'
SHOP_TEL = 'telephone'
SHOP_LNG = 'shop_lng'
SHOP_LAT = 'shop_lat'
DEAL_ORIGIN_PRICE = 'origin_price'
HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'xapian'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 27 
HAYSTACK_XAPIAN_PATH = os.path.join(CURRENT_PATH, 'tuangou_index')
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
CITY_TUPLE = (CITY_NAME, CITY_API_NAME)
LOG_PATH = os.path.join(CURRENT_PATH, 'log')
ERROR_LOG_FILE = os.path.join(LOG_PATH, 'app_err.log')
DEAL_SORTED_NUM = 60000
LIMIT_LENGTH = 6
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'guest'
BROKER_PASSWORD = 'guest'
BROKER_VHOST = '/'
CACHE_BACKEND = "memcached://127.0.0.1:11211/"
CELERY_DISABLE_RATE_LIMITS = True
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1
CITY_COOKIE_NAME = 'cookie_city'
LOGIN_REDIRECT = '/'
LIST_PER_PAGE = 48
WISH_PER_PAGE = 5
SPIDER_ERROR_LOG = os.path.join(LOG_PATH, 'error.txt')
WISHLIST_LIMIT = 100
LOGIN_URL = '/accounts/signin/'
PRICE_RANGE = {'1':'',
               '2':(0, 10), 
               '3':(10, 50),
               '4':(50, 100),
               '5':100,
}
PER_PAGE_COMMENTS = 5
QUERY_DB = os.path.join(CURRENT_PATH, 'querydb/QQWry.Dat')
SITE_AUDIT_LOG_FILE = 'audit_site.txt'
AUDIT_DIR_NAME = 'audit_data'
AUDIT_DATA_PATH = os.path.join(CURRENT_PATH, AUDIT_DIR_NAME)
PICK_DIR_NAME = 'pickle_data'
NORMAL = 1 
MULTIMEDIA = 2 
STORE_FETCH_TYPE = (NORMAL, MULTIMEDIA)
SELLER_CHART = 10
VIEW_CHART = 10
THUMB_WIDTH = 90
THUMB_HEIGHT = 60
LOGO_WIDTH = 120
LOGO_HEIGHT = 120
LOGO_SIZE_LIMIT = 200
AUTH_PROFILE_MODULE = 'accounts.userprofile'
AD_AUDIT = 'ad_pickle'
AD_INTERVAL = 10
AD_PREFETCH_ONE_TIME = 10
EMAIL_HOST = '127.0.0.1'
#EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 25
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'service@laidian.com'
#EMAIL_HOST_USER = 'b.zougang@gmail.com'
SERVER_EMAIL = 'service@laidiantuan.com'
EMAIL_HOST_USER = 'service'
EMAIL_HOST_PASSWORD = 'yitangservice'
#EMAIL_HOST_PASSWORD = '359948635'
#EMAIL_USE_TLS = True
#EMAIL_TLS = True
EMAIL_DEBUG = False
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEAL_PER_ROW = 4
CITY_DEAL_PER_ROW = 3
ORDINARY_SITE_OFFSET = 7
RUN_FLAG_FILE = os.path.join(CURRENT_PATH, 'custom_flag.txt')
CLOSE_FLAG_FILE = os.path.join(CURRENT_PATH, 'close_flag.txt')
#CANON_URLS_TO_REWRITE = ['laidiantuan.com']
#CANON_URL_HOST = 'www.laidiantuan.com'
ROWS_MAP = {'meishitianxia': [6, 3, 'd'], 'xiuxianyule':[4, 3,'e'], 'meirongyangsheng':[3, 3, 'f'], 'jiudianlvyou':[1, 4, 'i'], 'huazhuangpin':[2, 4, 'g'], u'fuzhuangshipin':[2, 4, 'h'], 'riyongjiaju':[1, 4, 'j']}
SEARCH_ENGINE = { 
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)":"baidu",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)": "google",
    "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)": "sogou",
    "www.baidu.com":'baidu', 
    "www.google.com":"google", 
    "www.yahoo.com":"yahoo", 
    "www.sogou.com":"sogou", 
    "www.sina.com":"sina", 
    "so.163.com":"wangyi", 
}
OBJECT_TIMEOUT = 12 * 60 * 60
OBJECTS_TIMEOUT =  3 * 60 * 60
OBJECT_LIST_TIMEOUT = 12 * 60 * 60
OBJECT_TUPLE_TIMEOUT = 12 * 60 * 60
APP_LIST_PER_PAGE = 12
APP_ACCESS_LOG = 'app_access.log'
CACHE_PAGE_NUMBER = 10
PAGE_COUNTER_FILE = '%s_sum.pk'
APP_CLICK_LOG = '%s.pk'
CLICK_COUNTER_FILE = 'clicktotal.txt'
SEO_KEYWORDS = {'meishitianxia': u'美食', 'xiuxianyule': u'娱乐', 'rihanyaxi': u'日式韩系', 'xicanguoji': u'西餐', 'huoguoshaokao': u'火锅', 'xiuxiankuaican':u'快餐', 'dangaotianpin': u'蛋糕', 'haixian': u'海鲜', 'zizhu': u'自助', 'qitameishiyinpin': u'美食', 'dianyingyanchu': u'电影', 'juhuihuanchang': u'KTV', 'sheyingxiezhen': u'摄影', 'wenyuanxiyu':u'洗浴', 'yundongjianshen': u'健身','qitayule': u'娱乐'} 
