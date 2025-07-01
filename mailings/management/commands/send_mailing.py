from django.core.management.base import BaseCommand

from mailings.models import Mailing


class Command(BaseCommand):
    """Класс наследуется от BaseCommand, используется для создания консольных команд, вызываемых через manage.py,
        здесь используется для отправки рассылки по требованию"""
    help = "Отправляет рассылку по требованию"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int, help="ID рассылки")

    def handle(self, *args, **kwargs):
        mailing_id = kwargs["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)

            if mailing.status_mailing == Mailing.COMPLETED_AT:
                self.stdout.write(self.style.WARNING("Рассылка уже была отправлена ранее"))
                return

            success, message = mailing.send_mailing()

            if success:
                self.stdout.write(self.style.SUCCESS(message))
            else:
                self.stdout.write(self.style.ERROR(message))

        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))
