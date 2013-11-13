import os, sys 
# path to directory of the .wsgi file('apache/')
wsgi_dir = os.path.abspath(os.path.dirname(__file__))
#path to project root directory (parent of 'apache/')
project_dir = os.path.dirname(wsgi_dir)

sys.path.append(project_dir)
root_project = os.path.dirname(project_dir)
sys.path.append(root_project)

#add the settings.py file to your system's PATH
settings = os.path.join(project_dir, 'settings')

# PYTHON_EGG_CACHE variable$
os.environ['PYTHON_EGG_CACHE'] = '%s/PYTHON_EGG_CACHE' % '/tmp'

#explicitly define the DJANGO_SETTINGS_MODULE
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
