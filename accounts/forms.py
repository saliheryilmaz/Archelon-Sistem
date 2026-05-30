from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import CustomUser


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Kullanıcı adı',
        widget=forms.TextInput(attrs={'placeholder': 'kullaniciadi', 'autofocus': True, 'class': 'form-input'})
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': 'form-input'})
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Ad', max_length=50)
    last_name = forms.CharField(label='Soyad', max_length=50)
    phone = forms.CharField(label='Telefon', max_length=20, required=False)
    birth_date = forms.DateField(
        label='Doğum tarihi',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(label='Ad', max_length=50)
    last_name = forms.CharField(label='Soyad', max_length=50)
    phone = forms.CharField(label='Telefon', max_length=20, required=False)
    birth_date = forms.DateField(
        label='Doğum tarihi',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_MEMBER
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    swim_level = forms.IntegerField(
        label='Yüzme seviyesi',
        required=False,
        min_value=1,
        max_value=10,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        widget=forms.NumberInput(attrs={'type': 'number', 'min': '1', 'max': '10', 'placeholder': '1–10'}),
        help_text='1 = başlangıç, 10 = ileri seviye'
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'role', 'swim_level', 'is_active')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-input')
