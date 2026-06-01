from django.db import models
from django.conf import settings


class PackageType(models.Model):
    KURSIYER = 'kursiyer'
    KURSIYER_4 = 'kursiyer_4'
    OZEL_DERS = 'ozel_ders'
    DENEME_DERSI = 'deneme_dersi'

    TYPE_CHOICES = [
        (KURSIYER, 'Kursiyer (8 Seans)'),
        (KURSIYER_4, 'Kursiyer (4 Seans)'),
        (OZEL_DERS, 'Özel Ders'),
        (DENEME_DERSI, 'Deneme Dersi'),
    ]

    DEFAULT_SESSIONS = {
        KURSIYER: 8,
        KURSIYER_4: 4,
        OZEL_DERS: 8,
        DENEME_DERSI: 1,
    }

    slug = models.CharField('Tip', max_length=20, choices=TYPE_CHOICES, unique=True)
    name = models.CharField('Ad', max_length=100)
    session_count = models.PositiveIntegerField('Seans sayısı')
    description = models.TextField('Açıklama', blank=True)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        verbose_name = 'Paket türü'
        verbose_name_plural = 'Paket türleri'
        ordering = ['session_count']

    def __str__(self):
        return f'{self.name} ({self.session_count} seans)'

    @classmethod
    def get_or_create_defaults(cls):
        defaults = [
            (cls.DENEME_DERSI, 'Deneme Dersi',      1, 'Tek seferlik deneme dersi.'),
            (cls.KURSIYER_4,   'Kursiyer (4 Seans)', 4, 'Temel yüzme eğitimi paketi (4 seans).'),
            (cls.KURSIYER,     'Kursiyer (8 Seans)', 8, 'Temel yüzme eğitimi paketi (8 seans).'),
            (cls.OZEL_DERS,    'Özel Ders',          8, 'Birebir özel yüzme dersi paketi.'),
        ]
        for slug, name, count, desc in defaults:
            cls.objects.update_or_create(slug=slug, defaults={
                'name': name, 'session_count': count, 'description': desc
            })
        # Aqua Fitness varsa pasife al
        cls.objects.filter(slug='aqua_fitness').update(is_active=False)


class UserPackage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='packages',
        verbose_name='Üye'
    )
    package_type = models.ForeignKey(
        PackageType,
        on_delete=models.PROTECT,
        verbose_name='Paket türü'
    )
    total_sessions = models.PositiveIntegerField('Toplam seans')
    remaining_sessions = models.PositiveIntegerField('Kalan seans')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_packages',
        verbose_name='Atayan'
    )
    assigned_at = models.DateTimeField('Atanma tarihi', auto_now_add=True)
    expires_at = models.DateField('Bitiş tarihi', null=True, blank=True)
    start_time = models.TimeField('Başlangıç saati', null=True, blank=True)
    payment_date = models.DateField('Ödeme tarihi', null=True, blank=True)
    is_active = models.BooleanField('Aktif', default=True)
    notes = models.TextField('Notlar', blank=True)

    class Meta:
        verbose_name = 'Üye paketi'
        verbose_name_plural = 'Üye paketleri'
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.user} — {self.package_type.name} ({self.remaining_sessions}/{self.total_sessions})'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.total_sessions = self.package_type.session_count
            self.remaining_sessions = self.package_type.session_count
        super().save(*args, **kwargs)

    @property
    def used_sessions(self):
        return self.total_sessions - self.remaining_sessions

    @property
    def progress_percent(self):
        if self.total_sessions == 0:
            return 0
        return int((self.remaining_sessions / self.total_sessions) * 100)

    @property
    def status_class(self):
        pct = self.progress_percent
        if pct == 0:
            return 'danger'
        if pct <= 25:
            return 'warning'
        return 'success'

    def use_session(self):
        if self.remaining_sessions > 0:
            self.remaining_sessions -= 1
            self.save(update_fields=['remaining_sessions'])
            return True
        return False

    def refund_session(self):
        if self.remaining_sessions < self.total_sessions:
            self.remaining_sessions += 1
            self.save(update_fields=['remaining_sessions'])
