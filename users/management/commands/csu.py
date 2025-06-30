from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Класс наследуется от BaseCommand, используется для создания консольных команд, вызываемых через manage.py,
        здесь используется для создания суперпользователя"""

    def handle(self, *args, **options):
        user = User.objects.create(email="admin@example.com")
        user.set_password("123qwe")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
