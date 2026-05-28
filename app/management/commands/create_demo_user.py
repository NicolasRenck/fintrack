from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Cria o usuário demo'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@fintrack.com', 'demofintrack123')
            self.stdout.write('Usuário demo criado com sucesso.')
        else:
            self.stdout.write('Usuário demo já existe.')