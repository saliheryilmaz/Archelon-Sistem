from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Instructor(models.Model):
    name = models.CharField('Ad Soyad', max_length=100)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        verbose_name = 'Eğitmen'
        verbose_name_plural = 'Eğitmenler'
        ordering = ['name']

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Beklemede'),
        (STATUS_CONFIRMED, 'Onaylı'),
        (STATUS_CANCELLED, 'İptal'),
        (STATUS_COMPLETED, 'Tamamlandı'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Üye'
    )
    user_package = models.ForeignKey(
        'packages.UserPackage',
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name='Kullanılan paket'
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name='Eğitmen'
    )
    date = models.DateField('Tarih')
    start_time = models.TimeField('Başlangıç saati')
    end_time = models.TimeField('Bitiş saati')
    status = models.CharField('Durum', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    attended = models.BooleanField('Geldi', null=True, blank=True, default=None)
    notes = models.TextField('Notlar', blank=True)
    created_at = models.DateTimeField('Oluşturulma', auto_now_add=True)

    class Meta:
        verbose_name = 'Randevu'
        verbose_name_plural = 'Randevular'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.user} — {self.date} {self.start_time}'

    def clean(self):
        if self.user_package_id and self.pk is None:
            if self.user_package.remaining_sessions <= 0:
                raise ValidationError('Bu pakette kalan seans hakkı bulunmuyor.')
            if self.user_id and self.user_package.user_id != self.user_id:
                raise ValidationError('Bu paket bu üyeye ait değil.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Seans hakkı artık onay anında düşer, burada düşürülmez.

    def confirm(self):
        """Admin onaylar: durumu güncelle ve seans hakkını düşür."""
        if self.status == self.STATUS_PENDING:
            if self.user_package.remaining_sessions <= 0:
                raise ValidationError('Bu pakette kalan seans hakkı bulunmuyor.')
            self.status = self.STATUS_CONFIRMED
            self.save(update_fields=['status'])
            self.user_package.use_session()

    def cancel(self):
        if self.status not in (self.STATUS_CANCELLED, self.STATUS_COMPLETED):
            was_confirmed = self.status == self.STATUS_CONFIRMED
            self.status = self.STATUS_CANCELLED
            self.save(update_fields=['status'])
            # Seans iadesi yalnızca onaylanmış randevularda yapılır
            if was_confirmed:
                self.user_package.refund_session()

    @property
    def status_badge(self):
        return {
            self.STATUS_PENDING: 'warning',
            self.STATUS_CONFIRMED: 'success',
            self.STATUS_CANCELLED: 'danger',
            self.STATUS_COMPLETED: 'info',
        }.get(self.status, 'secondary')
