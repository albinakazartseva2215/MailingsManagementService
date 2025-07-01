from django.forms import ModelForm, BooleanField

from mailings.models import Recipient, Message, Mailing, MailingAttempt


class StyleFormMixin:
    """Класс-миксин, который используется для стилизации в других классах-формах"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fiеld_name, fiеld in self.fields.items():
            if isinstance(fiеld, BooleanField):
                fiеld.widget.attrs["class"] = "form-check-input"
            else:
                fiеld.widget.attrs["class"] = "form-control"


class RecipientForm(StyleFormMixin, ModelForm):
    """Класс используется для создания формы на основании модели Recipient"""
    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        model = Recipient
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner_recipient = self.user
        if commit:
            instance.save()
        return instance


class MessageForm(StyleFormMixin, ModelForm):
    """Класс используется для создания формы на основании модели Message"""
    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        model = Message
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.owner_recipient = self.user
        if commit:
            instance.save()
        return instance


class MailingForm(StyleFormMixin, ModelForm):
    """Класс используется для создания формы на основании модели Mailing"""

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        model = Mailing
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Безопасно извлекаем request
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if request:
            # Фильтрация получателей
            if request.user.has_perm('mailings.view_all_recipients'):
                self.fields['recipient'].queryset = Recipient.objects.all()
            else:
                self.fields['recipient'].queryset = Recipient.objects.filter(
                    owner_recipient=request.user
                )

            # Фильтрация сообщений
            if request.user.has_perm('mailings.view_all_messages'):
                self.fields['message'].queryset = Message.objects.all()
            else:
                self.fields['message'].queryset = Message.objects.filter(
                    owner_message=request.user
                )


class MailingAttemptForm(StyleFormMixin, ModelForm):
    """Класс используется для создания формы на основании модели MailingAttempt"""
    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        model = MailingAttempt
        fields = '__all__'
