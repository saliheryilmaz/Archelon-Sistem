from django import forms
from django.utils import timezone
from .models import Appointment, Instructor
from packages.models import UserPackage
from accounts.models import CustomUser


class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        label='Tarih',
        widget=forms.DateInput(attrs={'type': 'date', 'min': str(timezone.now().date())}),
    )
    start_time = forms.TimeField(
        label='Başlangıç saati',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    end_time = forms.TimeField(
        label='Bitiş saati',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )

    class Meta:
        model = Appointment
        fields = ('user_package', 'instructor', 'date', 'start_time', 'end_time', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_package'].queryset = UserPackage.objects.filter(
            user=user, is_active=True, remaining_sessions__gt=0,
            package_type__slug='ozel_ders'
        ).select_related('package_type')
        self.fields['user_package'].label = 'Paket'
        self.fields['user_package'].empty_label = '— Paket seçin —'
        self.fields['instructor'].queryset = Instructor.objects.filter(is_active=True)
        self.fields['instructor'].label = 'Eğitmen (isteğe bağlı)'
        self.fields['instructor'].required = False
        self.fields['instructor'].empty_label = '— Eğitmen seçin —'
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('Bitiş saati başlangıç saatinden sonra olmalıdır.')
        return cleaned


class AdminAppointmentForm(forms.ModelForm):
    """Admin tarafından herhangi bir üye için randevu oluşturma formu."""

    member = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True, role='member').order_by('first_name', 'last_name'),
        label='Üye',
        empty_label='— Üye seçin —',
    )
    date = forms.DateField(
        label='Tarih',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    start_time = forms.TimeField(
        label='Başlangıç saati',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )
    end_time = forms.TimeField(
        label='Bitiş saati',
        widget=forms.TimeInput(attrs={'type': 'time'}),
    )

    class Meta:
        model = Appointment
        fields = ('instructor', 'date', 'start_time', 'end_time', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = Instructor.objects.filter(is_active=True)
        self.fields['instructor'].label = 'Eğitmen (isteğe bağlı)'
        self.fields['instructor'].required = False
        self.fields['instructor'].empty_label = '— Eğitmen seçin —'
        self.fields['notes'].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and end <= start:
            raise forms.ValidationError('Bitiş saati başlangıç saatinden sonra olmalıdır.')
        return cleaned


class InstructorAssignForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('instructor',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = Instructor.objects.filter(is_active=True)
        self.fields['instructor'].label = 'Eğitmen (isteğe bağlı)'
        self.fields['instructor'].required = False
        self.fields['instructor'].empty_label = '— Eğitmen seçin —'
        self.fields['instructor'].widget.attrs['class'] = 'form-input'


class InstructorForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ('name', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Ad Soyad'
        self.fields['name'].widget.attrs['class'] = 'form-input'
        self.fields['is_active'].label = 'Aktif'
