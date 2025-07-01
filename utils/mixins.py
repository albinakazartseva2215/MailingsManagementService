from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView


class ManagerRequiredMixin(LoginRequiredMixin):
    """Базовый миксин для проверки прав менеджера"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Проверяем наличие хотя бы одного права менеджера
        if not any([
            request.user.has_perm('users.blocked_users'),
            request.user.has_perm('mailings.block_mailing'),
            request.user.has_perm('users.view_all_users'),
        ]):
            raise PermissionDenied("Только менеджеры имеют доступ к этой странице")

        return super().dispatch(request, *args, **kwargs)


class OwnerOrManagerMixin(LoginRequiredMixin):
    """Миксин для проверки владельца или прав менеджера"""

    def dispatch(self, request, *args, **kwargs):
        # Для ListView - пропускаем проверку объекта
        if isinstance(self, ListView):
            return super().dispatch(request, *args, **kwargs)

        try:
            obj = self.get_object()
        except AttributeError:
            # Если get_object недоступен, пропускаем проверку объекта
            return super().dispatch(request, *args, **kwargs)

        # Для моделей с явным владельцем
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return super().dispatch(request, *args, **kwargs)

        # Для моделей с разными полями владельца
        owner_fields = ['owner_recipient', 'owner_message', 'owner_mailing', 'owner_attempt']
        for field in owner_fields:
            if hasattr(obj, field) and getattr(obj, field) == request.user:
                return super().dispatch(request, *args, **kwargs)

        # Проверка прав менеджера
        if any([
            request.user.has_perm('mailings.view_all_mailings'),
            request.user.has_perm('mailings.view_all_recipients'),
            request.user.has_perm('mailings.view_all_messages'),
        ]):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("У вас нет прав доступа к этому объекту")
