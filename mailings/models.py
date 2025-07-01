from django.utils import timezone

from django.core.mail import send_mail
from django.db import models

from config import settings
from users.models import User

import logging

logger = logging.getLogger(__name__)


class Recipient(models.Model):
    """Модель получателя рассылок с заданными полями и мета классом"""
    recipient_email = models.EmailField(unique=True, verbose_name="Email", help_text="Введите email")
    full_name = models.CharField(max_length=250, verbose_name="Ф.И.О.", help_text="Введите Ф.И.О.", blank=True,
                                 null=True)
    comment = models.TextField(verbose_name="Комментарий", help_text="Введите комментарий", blank=True, null=True)
    owner_recipient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owner_recipient",
        verbose_name="Владелец получателя сообщения",
    )

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("view_all_recipients", "Может просматривать всех получателей"),
        ]

    def __str__(self):
        """Строковое представление класса"""
        return f"Получатель рассылки: {self.recipient_email}"


class Message(models.Model):
    """Модель сообщения с заданными полями и мета классом"""
    subject = models.CharField(max_length=100, verbose_name="Тема письма", help_text="Введите тему письма")
    body = models.TextField(verbose_name="Тело письма", help_text="Введите текст письма", blank=True, null=True)
    owner_message = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owner_message",
        verbose_name="Владелец сообщения",
    )

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("view_all_messages", "Может просматривать все сообщения"),
        ]

    def __str__(self):
        """Строковое представление класса"""
        return f"Тема сообщения: {self.subject}"


class Mailing(models.Model):
    """Модель рассылки с заданными полями и мета классом"""
    COMPLETED_AT = "completed"
    CREATED_AT = "created"
    LAUNCHED_AT = "launched"
    BLOCKED = "blocked"

    STATUS_CHOICES = [
        (COMPLETED_AT, "Завершена"),
        (CREATED_AT, "Создана"),
        (LAUNCHED_AT, "Запущена"),
        (BLOCKED, "Отключена"),
    ]
    datetime_start = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время первой отправки",
                                          help_text="Введите дату и время первой отправки", blank=True, null=True)
    datetime_end = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время окончания отправки",
                                        help_text="Введите дату и время окончания отправки", blank=True, null=True)
    status_mailing = models.CharField(
        max_length=9,
        choices=STATUS_CHOICES,
        default=CREATED_AT,
        verbose_name="Статус рассылки",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="message",
        verbose_name="Сообщение",
    )
    recipient = models.ManyToManyField(Recipient, related_name="recipients", verbose_name="Получатели")
    owner_mailing = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owner_mailing",
        verbose_name="Владелец рассылки",
    )

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("block_mailing", "Может блокировать рассылки"),
            ("view_all_mailings", "Может просматривать все рассылки"),
        ]

    def __str__(self):
        """Строковое представление класса"""
        return f"Рассылка {self.datetime_start} со статусом {self.status_mailing}"

    def send_messages(self):
        # Проверка, не отключена ли рассылка
        if self.status_mailing == self.BLOCKED:
            logger.error(f"Рассылка {self.id} отключена менеджером")
            return False
        # Проверка наличия сообщения и получателей
        if not hasattr(self, 'message') or not self.message:
            logger.error("Рассылка без сообщения")
            return False

        if not self.recipient.exists():
            logger.error("Нет получателей")
            return False

        # Меняем статус на "Запущена" перед началом отправки
        self.status_mailing = self.LAUNCHED_AT
        self.save(update_fields=['status_mailing'])
        logger.info(f"Статус рассылки {self.id} изменен на 'Запущена'")

        from_email = settings.DEFAULT_FROM_EMAIL
        logger.info(f"Начало рассылки {self.id} для {self.recipient.count()} получателей")

        # Счетчики для статистики
        success_count = 0
        error_count = 0

        for recipient in self.recipient.all():
            try:
                # Отправка письма
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=from_email,
                    recipient_list=[recipient.recipient_email],
                    fail_silently=False
                )

                # Создаем успешную попытку
                MailingAttempt.objects.create(
                    mailing=self,
                    recipient=recipient,  # Добавляем получателя
                    status_attempt=MailingAttempt.SUCCESSFULLY,
                    datetime_attempt=timezone.now(),
                    response_mail_server="Успешно отправлено",
                    owner_attempt=self.owner_mailing
                )
                success_count += 1
                logger.info(f"Успешно отправлено на {recipient.recipient_email}")

            except Exception as e:
                # Создаем неудачную попытку
                MailingAttempt.objects.create(
                    mailing=self,
                    recipient=recipient,  # Добавляем получателя
                    status_attempt=MailingAttempt.UNSUCCESSFULLY,
                    datetime_attempt=timezone.now(),
                    response_mail_server=str(e)[:255],  # Ограничиваем длину сообщения
                    owner_attempt=self.owner_mailing
                )
                error_count += 1
                logger.error(f"Ошибка при отправке на {recipient.recipient_email}: {str(e)}")

        # Меняем статус на "Завершена" после окончания отправки
        self.status_mailing = self.COMPLETED_AT
        self.save(update_fields=['status_mailing'])
        logger.info(f"Рассылка {self.id} завершена. Успешно: {success_count}, Ошибок: {error_count}")

        return True


class MailingAttempt(models.Model):
    """Модель попытки рассылки с заданными полями и мета классом"""
    UNSUCCESSFULLY = "unsuccessfully"
    SUCCESSFULLY = "successfully"
    STATUS_CHOICES = [
        (SUCCESSFULLY, "Успешно"),
        (UNSUCCESSFULLY, "Не успешно"),
    ]
    datetime_attempt = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки",
                                            help_text="Введите дату и время попытки", blank=True, null=True)
    status_attempt = models.CharField(
        max_length=14,
        choices=STATUS_CHOICES,
        default=SUCCESSFULLY,
        verbose_name="Статус попытки рассылки",
    )
    response_mail_server = models.TextField(verbose_name="Ответ почтового сервера",
                                            help_text="Введите ответ почтового сервера", blank=True, null=True)
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="mailing",
        verbose_name="Рассылка",
    )
    owner_attempt = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owner_attempt",
        verbose_name="Владелец попытки рассылки",
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Получатель",
        related_name="attempts"
    )

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        verbose_name = "Попытка"
        verbose_name_plural = "Попытки"

    def __str__(self):
        """Строковое представление класса"""
        return f"Попытка рассылки {self.datetime_attempt} со статусом {self.status_attempt}"
