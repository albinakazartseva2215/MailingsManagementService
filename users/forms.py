from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django import forms
from django.forms import BooleanField

from users.models import User


class StyleFormMixin:
    """Класс-миксин, который используется для стилизации в других классах-формах"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fiеld_name, fiеld in self.fields.items():
            if isinstance(fiеld, BooleanField):
                fiеld.widget.attrs["class"] = "form-check-input"
            else:
                fiеld.widget.attrs["class"] = "form-control"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Класс используется для создания формы регистрации на основании модели User с заданными полями"""
    class Meta:
        model = User
        # exclude = ('created_at', 'updated_at')
        fields = ("email", "password1", "password2")


class UserProfileForm(forms.ModelForm, StyleFormMixin):
    class Meta:
        model = User
        fields = ["email", "avatar", "phone", "country", "token"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Этот email уже используется другим пользователем")
        return email


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
