from django import forms
from .models import UserPackage, PackageType
from accounts.models import CustomUser


class AssignPackageForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True, role='member').order_by('first_name'),
        label='Üye',
        empty_label='— Üye seçin —'
    )
    package_type = forms.ModelChoiceField(
        queryset=PackageType.objects.filter(is_active=True),
        label='Paket türü',
        empty_label='— Paket seçin —'
    )
    start_time = forms.TimeField(
        label='Başlangıç saati',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    payment_date = forms.DateField(
        label='Ödeme tarihi',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    expires_at = forms.DateField(
        label='Bitiş tarihi (isteğe bağlı)',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    notes = forms.CharField(
        label='Notlar (isteğe bağlı)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )

    class Meta:
        model = UserPackage
        fields = ('user', 'package_type', 'start_time', 'payment_date', 'expires_at', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
