import os
import time
from datetime import datetime
from PIL import Image
from django.conf import settings

def save_image(image, image_name, path):
    image_dirs = "%s/%s" % (settings.MEDIA_ROOT, path)
    if not os.path.exists(image_dirs):
        os.makedirs(image_dirs)
    image_path = os.path.join(image_dirs, image_name)
    if os.path.exists(image_path):
        name, ext = os.path.splitext(image_name)
        image_name = name + str(time.time()) + ext
        image_path = os.path.join(image_path, image_name)
    try:
        image.save(image_path, quality=100)
    except TypeError:
        image_name = image_name +'.'+ image.format
        image_path = os.path.join(image_path, image_name)
        image.save(image_name, quality=100)
    except  KeyError:
        image.save(image_path, 'JPEG', quality=100)
    except IOError:
        image.mode = 'RGB'
        image.save(image_path, quality=100)
    return "%s/%s" % (path, image_name)

def gen_resize_image(image):
    i_width = image.size[0]
    width = settings.LOGO_WIDTH
    if i_width > width:
        ratio = float(width)/i_width
        height = int(image.size[1] * ratio)
        image = image.resize((width, height), Image.BILINEAR)
    return image

def handle_upload_logo(f, request):
    now = datetime.now()
    image_sub_path = "%s/%s/%s/%s" % ('profiles', now.strftime('%Y'), now.strftime('%m'), now.strftime('%d'))
    image_dirs = '%s/%s' % (settings.MEDIA_ROOT, image_sub_path)
    if not os.path.exists(image_dirs):
        os.makedirs(image_dirs)
    image_name = f.name
    raw_image = os.path.join(image_dirs, image_name)
    if os.path.exists(raw_image):
        raw_path, image_name = raw_image.rsplit('/', 1)
        image_name, ext = os.path.splitext(image_name)
        image_name = image_name + str(time.time())+ext
        raw_image = os.path.join(raw_path, image_name)
    with open(raw_image, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    raw_image_path = os.path.join(image_sub_path, image_name)
    im = Image.open(raw_image)
    reim = gen_resize_image(im)
    image_name = 'logo' + image_name
    logo_path = save_image(reim, image_name, image_sub_path)
    return (raw_image_path, logo_path)
