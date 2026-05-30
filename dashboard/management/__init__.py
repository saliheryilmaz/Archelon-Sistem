"""
python manage.py kurulum
Veritabanı başlangıç verilerini oluşturur.
"""
from django.core.management.base import BaseCommand
from packages.models import PackageType
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Archeon başlangıç verilerini oluşturur (paket türleri + admin kullanıcısı)'

    def add_arguments(self, parser):
        parser.add_argument('--admin-user', default='admin')
        parser.add_argument('--admin-pass', default='archeon123')
        parser.add_argument('--admin-email', default='admin@archeon.com')

    def handle(self, *args, **options):
        self.stdout.write('Paket türleri oluşturuluyor...')
        PackageType.get_or_create_defaults()
        for pt in PackageType.objects.all():
            self.stdout.write(f'  ✓ {pt.name} — {pt.session_count} seans')

        username = options['admin_user']
        if not CustomUser.objects.filter(username=username).exists():
            self.stdout.write(f'Admin kullanıcısı oluşturuluyor: {username}')
            CustomUser.objects.create_superuser(
                username=username,
                email=options['admin_email'],
                password=options['admin_pass'],
                first_name='Admin',
                last_name='Archeon',
                role=CustomUser.ROLE_ADMIN,
            )
            self.stdout.write(f'  ✓ Kullanıcı adı: {username}')
            self.stdout.write(f'  ✓ Şifre: {options["admin_pass"]}')
        else:
            self.stdout.write(f'  → Admin zaten mevcut: {username}')

        self.stdout.write(self.style.SUCCESS('\nKurulum tamamlandı!'))
