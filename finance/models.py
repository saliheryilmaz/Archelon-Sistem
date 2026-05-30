from django.db import models
from django.conf import settings


class Transaction(models.Model):
    TYPE_INCOME = 'gelir'
    TYPE_EXPENSE = 'gider'
    TYPE_CHOICES = [
        (TYPE_INCOME, 'Gelir'),
        (TYPE_EXPENSE, 'Gider'),
    ]

    PAYMENT_CASH = 'nakit'
    PAYMENT_TRANSFER = 'havale'
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Nakit'),
        (PAYMENT_TRANSFER, 'Havale'),
    ]

    transaction_type = models.CharField('Tür', max_length=10, choices=TYPE_CHOICES)
    payment_method = models.CharField('Ödeme Yöntemi', max_length=10, choices=PAYMENT_CHOICES)
    amount = models.DecimalField('Tutar (₺)', max_digits=10, decimal_places=2)
    description = models.CharField('Açıklama', max_length=255)
    date = models.DateField('Tarih')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transactions',
        verbose_name='Kaydeden'
    )
    created_at = models.DateTimeField('Kayıt tarihi', auto_now_add=True)
    notes = models.TextField('Notlar', blank=True)

    class Meta:
        verbose_name = 'İşlem'
        verbose_name_plural = 'İşlemler'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.get_transaction_type_display()} — {self.description} — {self.amount}₺'
