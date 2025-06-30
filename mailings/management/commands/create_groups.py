from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing, Recipient, Message
from users.models import User


class Command(BaseCommand):
    help = 'Создает группы пользователей и назначает права'

    def handle(self, *args, **kwargs):
        # Создаем группы
        user_group, created = Group.objects.get_or_create(name='Пользователи')
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        # Получаем или создаем разрешения
        manager_permissions = []

        # Разрешения для модели User
        user_ct = ContentType.objects.get_for_model(User)
        perm, created = Permission.objects.get_or_create(
            codename='block_user',
            content_type=user_ct,
            defaults={'name': 'Может блокировать пользователей'}
        )
        manager_permissions.append(perm)

        perm, created = Permission.objects.get_or_create(
            codename='view_all_users',
            content_type=user_ct,
            defaults={'name': 'Может просматривать всех пользователей'}
        )
        manager_permissions.append(perm)

        # Разрешения для модели Recipient
        recipient_ct = ContentType.objects.get_for_model(Recipient)
        perm, created = Permission.objects.get_or_create(
            codename='view_all_recipients',
            content_type=recipient_ct,
            defaults={'name': 'Может просматривать всех получателей'}
        )
        manager_permissions.append(perm)

        # Разрешения для модели Message
        message_ct = ContentType.objects.get_for_model(Message)
        perm, created = Permission.objects.get_or_create(
            codename='view_all_messages',
            content_type=message_ct,
            defaults={'name': 'Может просматривать все сообщения'}
        )
        manager_permissions.append(perm)

        # Разрешения для модели Mailing
        mailing_ct = ContentType.objects.get_for_model(Mailing)
        perm, created = Permission.objects.get_or_create(
            codename='block_mailing',
            content_type=mailing_ct,
            defaults={'name': 'Может блокировать рассылки'}
        )
        manager_permissions.append(perm)

        perm, created = Permission.objects.get_or_create(
            codename='view_all_mailings',
            content_type=mailing_ct,
            defaults={'name': 'Может просматривать все рассылки'}
        )
        manager_permissions.append(perm)

        # Назначаем права группе менеджеров
        manager_group.permissions.set(manager_permissions)

        self.stdout.write(self.style.SUCCESS('Группы и права успешно созданы'))
