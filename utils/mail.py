#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Enhance Email Tools

This module improves django.core.mail to support HTML and Multipart mail,
which due to a bug in Python 2.4 requires a hack.

This module could be removed if `this patch`_ from Django ticket #1541 is
merged into Django trunk.

.. _`this patch`: http://code.djangoproject.com/attachment/ticket/1541/multipart_mail.diff
"""
import smtplib, rfc822
from django.conf import settings
from django.core.mail import BadHeaderError, SafeMIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
import cPickle as pickle
import copy


class SafeMIMEMultipart(MIMEMultipart):
    def __setitem__(self, name, val):
        """Forbids multi-line headers, to prevent header injection"""
        if '\n' in val or '\r' in val:
            raise BadHeaderError, \
                "Header values can't contain newlines (got %r for header %r)" % (val, name)
        MIMEMultipart.__setitem__(self, name, val)

def send_mail(subject, message, from_email, recipient_list, cc_list=[], extra={}, fail_silently=False,
        auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD,
        tls=getattr(settings, 'EMAIL_TLS', False), encoding=settings.DEFAULT_CHARSET):
    """Easy wrapper for sending a single message to a recipient list.
    
    All members of the recipient list will see the other recipients in
    the 'To' field.  Note that the message parameter can be either text
    or one of the SafeMIMExxx methods listed above.

    The "extra" argument is used for additional required message settings, with key, value pairs
    like { 'Bcc' : 'tim@exoweb.net' }
    """
    return send_mass_mail([[subject, message, from_email, recipient_list, cc_list]], extra,
        fail_silently, auth_user, auth_password, tls, encoding)


def send_mass_mail(datatuple, extra={}, fail_silently=False, auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD, tls=getattr(settings, 'EMAIL_TLS', False),
        encoding=settings.DEFAULT_CHARSET):
    """Sends a message to each receipient in list.
    
    Given a datatuple of (subject, message, from_email, recipient_list), sends
    each message to each recipient list. Returns the number of e-mails sent.
    
    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    Note that the message parameter can be either text or one of the
    SafeMIMExxx methods listed above.
    """
    try:
        SMTP = smtplib.SMTP
        if settings.EMAIL_DEBUG:
            SMTP = STMPMock
        server = SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.esmtp_features["auth"] = "LOGIN PLAIN"
        if tls:
            server.starttls()
            server.ehlo()
        if auth_user and auth_password:
            server.login(auth_user, auth_password)
    except:
        if fail_silently:
            return
        raise
    num_sent = 0

    for subject, message, from_email, recipient_list, cc_list in datatuple:
        if not recipient_list:
            continue
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        #################################################
        msg = None
        if isinstance(message, SafeMIMEText) or isinstance(message, SafeMIMEMultipart):
            ## Change below is important!
            ## msg does not act as a proper dictionary... msg['key'] = value does not
            ## reset the value for msg['key'], but adds to it!
            msg = copy.deepcopy(message)
        else:
            msg = SafeMIMEText(message.encode(encoding), 'plain', encoding)
        #################################################
        # TODO: we should encode header fields that aren't pure ASCII, see:
        # http://maxischenko.in.ua/blog/entries/103/python-emails-i18n/
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list)
        msg['Date'] = rfc822.formatdate()
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
            recipient_list.extend(cc_list)
        if extra:
            for key in extra.keys():
                msg[key] = extra[key]
        try:
            server.sendmail(from_email, recipient_list, msg.as_string())
            num_sent += 1
        except:
            if not fail_silently:
                raise
    try:
        server.quit()
    except:
        if fail_silently:
            return
        raise
    return num_sent


# TODO: Find a better way to save email mock data -- maybe database
# TODO: Support concurrent
class STMPMock(object):
    """A simple Mock STMP server"""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.emaildata = load_email_data()

    def login(self, auth_user, auth_password):
        self.auth_user = auth_user
        self.auth_password = auth_password

    def sendmail(self, from_email, recipient_list, msg):
        self.emaildata.data.insert(0, [from_email, recipient_list, msg])

    def starttls(self):
        pass
    ehlo = starttls

    def quit(self):
        save_email_data(self.emaildata)
        
class EmailData(object):
    """A simple wrapper for email list"""
    def __init__(self, data=None):
        if data is None:
            data = []
        self.data = data

    def encode(self):
        # Encode email data to pickle
        return pickle.dumps(self.data)

    def decode(cls, pickled):
        # Decode email data instance from pickled
        return EmailData(data=pickle.loads(pickled))
    decode = classmethod(decode)

#filename = settings.EMAIL_MOCK_DIR + 'email.txt'

def load_email_data():
    f = open(filename, 'r')
    pickled = f.read()
    f.close()
    if pickled:
        return EmailData.decode(pickled)
    else:
        return EmailData()

def save_email_data(emaildata):
    """Save email data to tempfile"""
    f = open(filename, 'w') # overwritten old data
    f.write(emaildata.encode())
    f.close()

def clean_email_data():
    """clean old data"""
    f = open(filename, 'w') # overwritten old data
    f.write('')
    f.close()
    
