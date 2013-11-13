# -*- coding:utf-8 -*-
from django.conf import settings
class AccountFeed(object):
    MODIFY_SUCCESS = '修改成功!'
    ERROR_PARAM = '错误输入！'
    PASSWORD_ERR = '密码输入错误!'
    PASSWORD_NOT_MATCH = '两次密码不匹配!'
    LOGO_ERR = '图片大小不能超过%s K' % str(settings.LOGO_SIZE_LIMIT)
    INVALID_IMG = '无效图片!'
    ACTIVED_USER = '您的用户已经激活!'
    REAPPLY_MESSAGE = '邮件已经发送到您的邮箱%s，请点击邮件中的链接来完成注册。如果5分钟后您的收件箱仍没有收到此邮件，请查看您的垃圾邮件。'
    VCODE_ERR="验证码出错，请重新输入！"
    ACTIVE_MSG_NO_LOGIN = '您的邮件地址已经验证,<a href="/accounts/signin/">请登录</a>' 
    ACTIVE_MSG = '您的邮件地址已经验证!'
    INVALID_KEY = '验证码已经过期,请重新获取验证码！'
    EMAIL_EXIST = '用户名已经存在'
    NICK_EXIST = '用户昵称已经存在'
    VALID_EMAIL = '用户名有效'
    VALID_NICK = '用户昵称有效'
    USER_FEED = '请用您的邮箱帐号注册'
    FMT_ERR = '用户名格式不正确'
    LOGIN_ERR = '用户名或者密码错误'
    COOKIE_ENABLE = '请开启浏览器的COOKIE'
