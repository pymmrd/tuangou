# -*- coding:utf-8 -*-
# Create your views here.
import os
import random
import cStringIO
from hashlib import md5
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm 
from django.core import urlresolvers
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from tuangou.accounts.forms import RegistrationForm, UserProfileForm, ImageCropForm, \
    email_re, SpanErrorList, AuthenticationForm
from tuangou.utils.location import get_current_city
from tuangou.utils.mail import send_mail
from tuangou.utils import app_error_log
from tuangou.accounts.feed import AccountFeed
from tuangou.accounts.models import UserProfile, TempKey
from tuangou.accounts.upload_image import handle_upload_logo
from tuangou.guider.models import City
from tuangou.wishlist.models import DealWish 
from tuangou.accounts.profile import retrieve
from tuangou.stats.utils.stats import recommended_from_search, get_recently_viewed 

ACTIVE_FLAG = "active_flag"
FORGOT_FLAG = "forgot_password"
ACTIVE_URL = '/accounts/verify-email/'

@app_error_log
def register(request, tmpl="registration/signup.html"):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = RegistrationForm(postdata, error_class=SpanErrorList)
        if postdata.get('verify_code') != request.session.get('vcode', None):
            error_msg = AccountFeed.VCODE_ERR
        else:
            if form.is_valid():
                form.save()
                un = postdata.get('username', '')
                pw = postdata.get('password1', '')
                from django.contrib.auth import login, authenticate
                new_user = authenticate(username=un, password=pw)
                if new_user:
                    login(request, new_user)
                    profile = retrieve(request)
                    profile.gender = form.cleaned_data['gender']
                    profile.save()
                    next = postdata.get('next', None)
                    if next :
                        redirect_url = urlresolvers.reverse('register_step_two') 
                    else:
                        redirect_url = urlresolvers.reverse('register_step_two') +'?next=%s' % next 
                    return HttpResponseRedirect(redirect_url)
    else:
        next = request.GET.get('next', '')
        form = RegistrationForm(initial={'next':next})
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@app_error_log
def check_username(request):
    username = request.POST.get('username') 
    match_user = email_re.match(username)
    if match_user is None:
       success = 'False'
       msg = AccountFeed.FMT_ERR
    else:
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            success = 'True'
            msg = AccountFeed.VALID_EMAIL
        else:
            success = 'False'
            msg = AccountFeed.EMAIL_EXIST
    response = simplejson.dumps({'success':success, 'msg':msg})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
        
@csrf_exempt
@app_error_log
def check_nickname(request):
    nickname = request.POST.get('nickname') 
    try:
        UserProfile.objects.get(nickname=nickname)
    except UserProfile.DoesNotExist:
        success = 'True'
        msg = AccountFeed.VALID_NICK
    else:
        success = 'False'
        msg = AccountFeed.NICK_EXIST
    response = simplejson.dumps({'success':success, 'msg':msg})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@csrf_exempt
@never_cache
@app_error_log
def signin(request, tmpl='registration/signin.html', redirect_field_name=REDIRECT_FIELD_NAME):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    login_error = request.session.get('login_error', None)
    if login_error:
        del request.session['login_error']
    if request.method == 'POST':
        postdata  = request.POST.copy()
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT
            next = redirect_to or  settings.LOGIN_REDIRECT
            from django.contrib.auth  import login
            login(request, form.get_user())
            response = HttpResponseRedirect(next)
            response.set_cookie("LDT-username", form.get_user().username)
            response.set_cookie('traking_id', '123456', max_age=30)
            return response
    else:
        form = AuthenticationForm(request)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@never_cache
@app_error_log
def signin_from_ajax(request, redirect_field_name=REDIRECT_FIELD_NAME):
    postdata  = request.POST.copy()
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
            redirect_to = settings.LOGIN_REDIRECT
        next = redirect_to or  settings.LOGIN_REDIRECT
        from django.contrib.auth  import login
        user = form.get_user()
        login(request, user)
        success = 'True'
        response = simplejson.dumps({'success':success, 'username':user.username})
    else:
        request.session['login_error'] = 'True'
        success = 'False'
        response = simplejson.dumps({'success':success})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')

@app_error_log
def logout(request, tmpl='tags/header.html'):
    from django.contrib.auth import logout
    logout(request)
    html = render_to_string(tmpl)
    response = simplejson.dumps({'html':html, 'success':'True'})
    return HttpResponse(response, content_type="application/javascript; charset=utf-8")
    
@app_error_log
def get_check_code_image(request, sessionname='vcode'):
    image_path = os.path.join(settings.MEDIA_ROOT, 'images/v1.jpg')
    #im = Image.new('RGB', (40,20),(255,255,255))
    im = Image.open(image_path)
    draw = ImageDraw.Draw(im)
    rand_str = md5(str(datetime.now())).hexdigest()[0:4]
    ttfpath = os.path.join(settings.MEDIA_ROOT, 'font/font.tty')
    draw.text((5,1), rand_str[0], font=ImageFont.truetype(ttfpath, random.randrange(20, 25)), fill=(0,0,0))
    draw.text((20,2), rand_str[1], font=ImageFont.truetype(ttfpath, random.randrange(20,25)),fill=(0,0,0))
    draw.text((40,2), rand_str[2], font=ImageFont.truetype(ttfpath, random.randrange(20,25)),fill=(0,0,0))
    draw.text((60,1), rand_str[3], font=ImageFont.truetype(ttfpath, random.randrange(20,25)),fill=(0,0,0))
    del draw 
    if sessionname:
        request.session[sessionname] = rand_str
    buf = cStringIO.StringIO()
    im.save(buf, 'gif')
    response = HttpResponse(buf.getvalue(), 'image/gif')
    return response

@csrf_exempt
@login_required
def modify_profile(request, tmpl='accounts/modify_profile.html'):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    wish_counter = DealWish.objects.filter(user=request.user).count()
    profile = retrieve(request)
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = UserProfileForm(request=request, data=postdata)
        if form.is_valid():
            division = form.cleaned_data.get('division', None)
            year = form.cleaned_data.get('year', None)
            month = form.cleaned_data.get('month', None)
            day = form.cleaned_data.get('day', None)
            try:
                birthday = datetime(year, month, day)
            except (ValueError, TypeError):
                birthday = None
            gender = form.cleaned_data['gender']
            profile.nickname = form.cleaned_data['nickname']
            profile.birthday = birthday
            profile.gender = gender
            try:
                division = City.objects.get(name=division.strip())
            except City.DoseNotExist:
                success = 'False'
                message = AccountFeed.ERROR_PARAM
            else:
                profile.division = division
                profile.save()
                success = 'True'
                message = AccountFeed.MODIFY_SUCCESS
        else:
            success = 'False'
            message = AccountFeed.ERROR_PARAM
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@login_required
def upload_user_logo(request, tmpl="accounts/upload_user_logo.html"):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    wish_counter = DealWish.objects.filter(user=request.user).count()
    profile = retrieve(request)
    if request.method == 'POST':
        if request.FILES:
            form = UserProfileForm(request, data=request.POST)
            if form.is_valid():
                raw_image, logo = handle_upload_logo(request.FILES['image'], request)
                profile.raw_image = raw_image
                profile.image = logo
                profile.save()
        else:
            form = ImageCropForm(data=request.POST)
            if form.is_valid():
                form.crop()
                logo=form.save()
                if logo:
                    os.remove(os.path.join(settings.MEDIA_ROOT, profile.image.name))
                    profile.image=logo
                    profile.save()
    else:
        form = UserProfileForm(request)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@csrf_exempt
@login_required
def modify_password(request, tmpl="accounts/modify_password.html"):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    wish_counter = DealWish.objects.filter(user=request.user).count()
    profile = retrieve(request)
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = PasswordChangeForm(user=user, data=postdata)
        if form.is_valid():
            form.save()
            success = 'True'
            message = AccountFeed.MODIFY_SUCCESS
        else:
            success = 'False'
            if form.errors.get('password2', None):
                message = AccountFeed.PASSWORD_NOT_MATCH
            else:
                message = AccountFeed.PASSWORD_ERR
    else:
        form = PasswordChangeForm(user=request.user)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

@login_required
def show_account(request, tmpl='accounts/show_account.html'):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    recently_views = get_recently_viewed(request)
    recommend_deals = recommended_from_search(request)
    wish_counter = DealWish.objects.filter(user=request.user).count()
    profile = retrieve(request)
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def register_step_two(request, tmpl="registration/register_step_two.html"):
    next  = request.GET.get('next', None)
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    if request.method == 'POST': 
        postdata = request.POST.copy()
        if postdata.get('verify_code') != request.session.get('vcode', None):
            form_msg = AccountFeed.VCODE_ERR 
        else:
            form = AuthenticationForm(data=postdata)
            if form.is_valid():
                user = form.get_user()
                if user.is_active:
                    msg = AccountFeed.ACTIVED_USER
                else:
                    send_welcome_email(request, user, u'欢迎您加入来点团网站',
                                   'accounts/emails/welcome.txt')
                    msg = AccountFeed.REAPPLY_MESSAGE % user.username 
    else:
        form = AuthenticationForm()
        user = request.user 
        if user.is_authenticated():
            send_welcome_email(request, user, u'欢迎您加入来点团网站',
                           'accounts/emails/welcome.txt')
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request))

def send_welcome_email(request, user, title, template):
    active_key = TempKey.objects.create_key(user, ACTIVE_FLAG)
    key = active_key.key
    active_url = "%s%s/" % (ACTIVE_URL, key)
    profile = retrieve(request)
    nickname = profile.nickname
    #msg = loader.get_template(template).render(context)
    msg = render_to_string(template, locals(), context_instance=RequestContext(request))
    #send_mail(title, msg.decode('utf-8'), settings.SERVER_EMAIL,
    #          [user.email], fail_silently=False, encoding='GB18030')
    send_mail(title, msg.decode('utf-8'), settings.SERVER_EMAIL,
              [user.username], fail_silently=False, encoding='GB18030')
    
@never_cache
def verify_email(request, key, tmpl='registration/verify_email.html'):
    city = get_current_city(request)
    slug = city.slug
    cname = city.name
    active_key = TempKey.objects.authenticate(key)
    if active_key:
        # key is still operational
        user = active_key.user
        user.is_active = True
        user.save()
        # delete old key
        active_key.delete()
        # add message
        msg = AccountFeed.ACTIVE_MSG
    else:
        # key is not active anymore
        # add message
        msg = AccountFeed.INVALID_KEY
        flag = 'INV'
        form = AuthenticationForm() 
    return render_to_response(tmpl, locals(), context_instance=RequestContext(request)) 

def get_login_status_box(request, tmpl="tags/login_status_box.html"):
    nickname = None
    if request.user.is_authenticated():
        profile = retrieve(request)
        nickname = profile.nickname
    html = render_to_string(tmpl, locals())
    response = simplejson.dumps({'html':html, 'username': request.user.username})
    return HttpResponse(response, content_type='application/javascript; charset=utf-8')
