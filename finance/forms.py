from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'payment_method', 'amount', 'description', 'date', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Açıklama girin'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ek notlar (isteğe bağlı)'}),
        }
        labels = {
            'transaction_type': 'Tür',
            'payment_method': 'Ödeme Yöntemi',
            'amount': 'Tutar (₺)',
            'description': 'Açıklama',
            'date': 'Tarih',
            'notes': 'Notlar',
        }
