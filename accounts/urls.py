from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views', 
    url(r'^get_check_code_image/$', 'get_check_code_image', name='get_check_code_image'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^get-login-box/$', 'get_login_status_box', name='get_login_status_box'),
    (r'^check-nickname/$', 'check_nickname'),
    (r'^check-username/$', 'check_username'),
    (r'^register/step-two/', 'register_step_two', {'tmpl': 'registration/register_step_two.html'}, 'register_step_two'),
    (r'^verify-email/(?P<key>.+)/$', 'verify_email', {'tmpl': 'registration/verify_email.html'}, 'verify_email'),
    (r'^signin/$', 'signin', {'tmpl': 'registration/signin.html'}, 'signin'),
    (r'^signup/$', 'register',{'tmpl': 'registration/signup.html'}, 'signup'),
    (r'^profile/$', 'show_account', {'tmpl': 'accounts/show_account.html'}, 'show_accounts'),
    (r'^signin-from-ajax', 'signin_from_ajax'),
    (r'^modify-profile/$', 'modify_profile', {'tmpl':'accounts/modify_profile.html'}, 'modify_profile'),
    (r'^modify-password/$', 'modify_password', {'tmpl':'accounts/modify_password.html'}, 'modify_password'),
    (r'^upload-user-logo/$', 'upload_user_logo', {'tmpl':'accounts/upload_user_logo.html'}, 'upload_user_logo'),
)

