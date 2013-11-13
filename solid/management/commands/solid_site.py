from django.conf import settings
from solid_utils import gen_dest_tmpl
from tuangou.guider.models import City, Website
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

def get_city():
    for city in City.actives.all():
        yield city

def solid_site(tmpl="dy_tags/sites.html"):
    for city in get_city():
        A_letter = Website.objects.values('name', 'pk').filter(slug__startswith='a', opened_city=city)
        B_letter = Website.objects.values('name', 'pk').filter(slug__startswith='b', opened_city=city)
        C_letter = Website.objects.values('name', 'pk').filter(slug__startswith='c', opened_city=city)
        D_letter = Website.objects.values('name', 'pk').filter(slug__startswith='d', opened_city=city)
        E_letter = Website.objects.values('name', 'pk').filter(slug__startswith='e', opened_city=city)
        F_letter = Website.objects.values('name', 'pk').filter(slug__startswith='f', opened_city=city)
        G_letter = Website.objects.values('name', 'pk').filter(slug__startswith='g', opened_city=city)
        H_letter = Website.objects.values('name', 'pk').filter(slug__startswith='h', opened_city=city)
        I_letter = Website.objects.values('name', 'pk').filter(slug__startswith='i', opened_city=city)
        J_letter = Website.objects.values('name', 'pk').filter(slug__startswith='j', opened_city=city)
        K_letter = Website.objects.values('name', 'pk').filter(slug__startswith='k', opened_city=city)
        L_letter = Website.objects.values('name', 'pk').filter(slug__startswith='l', opened_city=city)
        M_letter = Website.objects.values('name', 'pk').filter(slug__startswith='m', opened_city=city)
        N_letter = Website.objects.values('name', 'pk').filter(slug__startswith='n', opened_city=city)
        O_letter = Website.objects.values('name', 'pk').filter(slug__startswith='o', opened_city=city)
        P_letter = Website.objects.values('name', 'pk').filter(slug__startswith='p', opened_city=city)
        Q_letter = Website.objects.values('name', 'pk').filter(slug__startswith='q', opened_city=city)
        R_letter = Website.objects.values('name', 'pk').filter(slug__startswith='r', opened_city=city)
        S_letter = Website.objects.values('name', 'pk').filter(slug__startswith='s', opened_city=city)
        T_letter = Website.objects.values('name', 'pk').filter(slug__startswith='t', opened_city=city)
        U_letter = Website.objects.values('name', 'pk').filter(slug__startswith='u', opened_city=city)
        V_letter = Website.objects.values('name', 'pk').filter(slug__startswith='v', opened_city=city)
        W_letter = Website.objects.values('name', 'pk').filter(slug__startswith='w', opened_city=city)
        X_letter = Website.objects.values('name', 'pk').filter(slug__startswith='x', opened_city=city)
        Y_letter = Website.objects.values('name', 'pk').filter(slug__startswith='y', opened_city=city)
        Z_letter = Website.objects.values('name', 'pk').filter(slug__startswith='z', opened_city=city)
        if city.slug :
            dest_tmpl ="dy_tags/sites/%s_sites.html" % city.slug
            html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
            gen_dest_tmpl(html, dest_tmpl)
            solid_banner_site(city)

def solid_banner_site(city, tmpl="dy_tags/city_site.html"):
    sites = Website.actives.values('name', 'pk', 'weight').filter(opened_city=city).order_by('-weight')
    dest_tmpl="dy_tags/banner/%s_site.html" % city.slug
    html = render_to_string(tmpl, locals()).encode(settings.DEFAULT_CHARSET)
    gen_dest_tmpl(html, dest_tmpl)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        solid_site()
