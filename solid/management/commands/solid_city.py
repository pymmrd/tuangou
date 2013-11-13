from django.conf import settings
from solid_utils import gen_dest_tmpl
from tuangou.guider.models import City
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

def city_list():
    A_letter = City.actives.values('name', 'slug').filter(slug__startswith='a')
    B_letter = City.actives.values('name', 'slug').filter(slug__startswith='b')
    C_letter = City.actives.values('name', 'slug').filter(slug__startswith='c')
    D_letter = City.actives.values('name', 'slug').filter(slug__startswith='d')
    E_letter = City.actives.values('name', 'slug').filter(slug__startswith='e')
    F_letter = City.actives.values('name', 'slug').filter(slug__startswith='f')
    G_letter = City.actives.values('name', 'slug').filter(slug__startswith='g')
    H_letter = City.actives.values('name', 'slug').filter(slug__startswith='h')
    I_letter = City.actives.values('name', 'slug').filter(slug__startswith='i')
    J_letter = City.actives.values('name', 'slug').filter(slug__startswith='j')
    K_letter = City.actives.values('name', 'slug').filter(slug__startswith='k')
    L_letter = City.actives.values('name', 'slug').filter(slug__startswith='l')
    M_letter = City.actives.values('name', 'slug').filter(slug__startswith='m')
    N_letter = City.actives.values('name', 'slug').filter(slug__startswith='n')
    O_letter = City.actives.values('name', 'slug').filter(slug__startswith='o')
    P_letter = City.actives.values('name', 'slug').filter(slug__startswith='p')
    Q_letter = City.actives.values('name', 'slug').filter(slug__startswith='q')
    R_letter = City.actives.values('name', 'slug').filter(slug__startswith='r')
    S_letter = City.actives.values('name', 'slug').filter(slug__startswith='s')
    T_letter = City.actives.values('name', 'slug').filter(slug__startswith='t')
    U_letter = City.actives.values('name', 'slug').filter(slug__startswith='u')
    V_letter = City.actives.values('name', 'slug').filter(slug__startswith='v')
    W_letter = City.actives.values('name', 'slug').filter(slug__startswith='w')
    X_letter = City.actives.values('name', 'slug').filter(slug__startswith='x')
    Y_letter = City.actives.values('name', 'slug').filter(slug__startswith='y')
    Z_letter = City.actives.values('name', 'slug').filter(slug__startswith='z')
    #gen city header
    #tmpl="dy_tags/city_list.html"
    #html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    #gen_dest_tmpl(html, tmpl)
    #gen page of site index by city
    #tmpl="dy_tags/site_by_city.html"
    #html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    #gen_dest_tmpl(html, tmpl)
    #gen profile city
    #tmpl="dy_tags/site_by_city.html"
    #flag='select_for_profile.html'
    #html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    #gen_dest_tmpl(html, tmpl, flag)
    #gen classify category city list
    tmpl="dy_tags/classify_by_city.html"
    html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    gen_dest_tmpl(html, tmpl)
    #gen classify district city list
    tmpl="dy_tags/classify_district_by_city.html"
    html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    gen_dest_tmpl(html, tmpl)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        city_list()
