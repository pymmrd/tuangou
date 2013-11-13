# -*- coding:utf-8 -*-
import os
import re
import time 
from PIL import Image
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.forms.util import ErrorList
from tuangou.accounts.models import UserProfile
from tuangou.accounts.feed import AccountFeed

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

class RegistrationForm(forms.Form):
    """
        A form that creates a user, with no privileges, from the given username and password.
    """
    nickname = forms.CharField(label="用户昵称", max_length=30)
    password1 = forms.CharField(label="密码", widget=forms.PasswordInput)
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput,)
    username = forms.EmailField(label='用户名', max_length=75, required=True)
    gender = forms.IntegerField(required=False)
    next = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['value'] = AccountFeed.USER_FEED
        self.fields['username'].widget.attrs['class'] = 'username'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        match_user = email_re.match(username)
        if match_user is None:
            raise forms.ValidationError(AccountFeed.FMT_ERR)
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(AccountFeed.EMAIL_EXIST)

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        try:
            UserProfile.objects.get(nickname=nickname)
        except UserProfile.DoesNotExist:
            return nickname
        raise forms.ValidationError(AccountFeed.NICK_EXIST)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "") 
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(AccountFeed.PASSWORD_NOT_MATCH)
        return password2

    def save(self, commit=True):
        user = User()
        username = self.cleaned_data["username"]
        user.username = username 
        user.is_active = False
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            nickname = self.cleaned_data['nickname']
            profile = UserProfile(user=user, nickname=nickname)
            profile.save()
        return user

class UserProfileForm(forms.Form):
    nickname = forms.CharField(label="用户昵称", max_length=30, required=False)
    division = forms.CharField(required=False)
    year = forms.IntegerField(required=False)
    month = forms.IntegerField(required=False)
    day = forms.IntegerField(required=False)
    gender = forms.IntegerField(required=False)
    image  = forms.ImageField(required=False)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(self.__class__, self).__init__(*args, **kwargs)

    def clean_image(self):
        if self.request.FILES:
            im = self.request.FILES['image']
            if im.size > settings.LOGO_SIZE_LIMIT * 1024:
                raise forms.ValidationError(AccountFeed.LOGO_ERR)
            return self.cleaned_data

class ImageCropForm(forms.Form):
    x1 = forms.DecimalField(widget=forms.HiddenInput)
    y1 = forms.DecimalField(widget=forms.HiddenInput)
    x2 = forms.DecimalField(widget=forms.HiddenInput)
    y2 = forms.DecimalField(widget=forms.HiddenInput)
    imagefile = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_imagefile(self):
        try:
            self.img = Image.open(os.path.join(settings.MEDIA_ROOT, self.cleaned_data['imagefile']))
        except IOError:
            raise forms.ValidationError(AccountFeed.INVALID_IMG)
        return self.cleaned_data['imagefile']

    def gen_normal_image(self, image):
        i_width = int(image.size[0])
        width = settings.LOGO_WIDTH 
        if i_width > width:
            ratio = float(width)/ i_width
            height = int(int(image.size[1]) * ratio)
            image = image.resize((width, height), Image.BILINEAR)
        return image

    def crop(self):
        """
        crop the image to the user supplied coordinates
        """
        x1=self.cleaned_data['x1']
        x2=self.cleaned_data['x2']
        y1=self.cleaned_data['y1']
        y2=self.cleaned_data['y2']
        self.img = self.img.crop((x1, y1, x2, y2))
        self.img = self.gen_normal_image(self.img)
    
    def save(self):
        from tuangou.accounts.upload_image import save_image
        image_sub_path, filename = self.cleaned_data['imagefile'].rsplit('/', 1)
        image_name = 'crop'+str(time.time())+ filename
        logo_path = save_image(self.img, image_name, image_sub_path)
        return logo_path

class SpanErrorList(ErrorList):
    def __unicode__(self):
        return self.as_span()

    def as_span(self):
        if not self: 
            return u'' 
        return u'<span class="highlight">%s</span>' % ''.join([e for e in self])

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(label='用户名', max_length=30)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(AccountFeed.LOGIN_ERR)
        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(AccountFeed.COOKIE_ENABLE)
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
