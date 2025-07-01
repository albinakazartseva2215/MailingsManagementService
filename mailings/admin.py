from django.contrib import admin

from mailings.models import Recipient, Mailing, Message, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Класс администрирования позволяет контролировать отображение и поведение модели Recipient
    в интерфейсе администратора"""
    # какие поля будут показаны в списке объектов
    list_display = (
        "id",
        "recipient_email",
        "owner_recipient",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Класс администрирования позволяет контролировать отображение и поведение модели Mailing
        в интерфейсе администратора"""
    # какие поля будут показаны в списке объектов
    list_display = (
        "id",
        "datetime_start",
        "status_mailing",
        "message",
        "owner_mailing"
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс администрирования позволяет контролировать отображение и поведение модели Message
        в интерфейсе администратора"""
    # какие поля будут показаны в списке объектов
    list_display = (
        "id",
        "subject",
        "owner_message",
    )


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Класс администрирования позволяет контролировать отображение и поведение модели MailingAttempt
        в интерфейсе администратора"""
    # какие поля будут показаны в списке объектов
    list_display = (
        "id",
        "status_attempt",
        "owner_attempt",
        "recipient",
        "datetime_attempt"
    )
