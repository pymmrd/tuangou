import os
from django.conf import settings

def gen_dest_tmpl(html, tmpl, flag=None):
    tmpl = tmpl.replace('dy_tags', 'tags')
    sub_dir, filename = tmpl.rsplit('/', 1)
    if flag:
        filename = flag
    tmpl_dir = os.path.join(settings.TEMPLATE_DIRS[0], sub_dir) 
    if not os.path.exists(tmpl_dir):
        os.makedirs(tmpl_dir)
    with open(os.path.join(tmpl_dir, filename), 'w') as f:
        f.write(html)
        
