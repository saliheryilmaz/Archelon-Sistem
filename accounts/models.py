from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_MEMBER = 'member'
    ROLE_INSTRUCTOR = 'instructor'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_MEMBER, 'Üye'),
        (ROLE_INSTRUCTOR, 'Eğitmen'),
        (ROLE_ADMIN, 'Admin'),
    ]

    phone = models.CharField('Telefon', max_length=20, blank=True)
    birth_date = models.DateField('Doğum tarihi', null=True, blank=True)
    role = models.CharField('Rol', max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    swim_level = models.PositiveSmallIntegerField(
        'Yüzme seviyesi',
        null=True,
        blank=True,
        help_text='1 (başlangıç) — 10 (ileri seviye)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return f'{self.get_full_name() or self.username}'

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN or self.is_staff

    @property
    def is_instructor_role(self):
        return self.role == self.ROLE_INSTRUCTOR

    @property
    def initials(self):
        parts = (self.get_full_name() or self.username).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return self.username[:2].upper()
