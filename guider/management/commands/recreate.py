from django.core.management.base import NoArgsCommand, CommandError
from tuangou.guider.models import ReDeal, Category

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        dianying = Category.objects.get(slug='menpiaojiaoyou')
        saishiyanchu = Category.objects.get(slug='youleyouyi')
        for word in dianying.matchwords.all():
            saishiyanchu.matchwords.add(word)
            
        



