from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, TemplateView, ListView
from django.contrib import messages

from config import settings
from mailings.forms import RecipientForm, MessageForm, MailingForm
from mailings.models import Recipient, Message, Mailing, MailingAttempt
from utils.mixins import ManagerRequiredMixin, OwnerOrManagerMixin
from utils.services import get_cached_messages


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания получателя рассылки"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RecipientUpdateView(UpdateView):
    """Класс для редактирования получателя рассылки"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:recipient_detail')

    def get_context_data(self, **kwargs):
        """Переопределенный метод добавляет пользовательские данные в контекст,
        который передаётся в шаблон при рендеринге"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Редактирование получателя рассылки: {self.object.recipient_email}"
        return context

    def get_success_url(self):
        return reverse_lazy('mailings:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientDetailView(DetailView):
    """Класс просмотра отдельного получателя рассылки"""
    model = Recipient
    context_object_name = 'recipient'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class RecipientDeleteView(DeleteView):
    """Класс удаления отдельного получателя рассылки"""
    model = Recipient
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class RecipientListView(OwnerOrManagerMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        if self.request.user.has_perm('mailings.view_all_recipients'):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner_recipient=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания сообщения"""
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner_message = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    """Класс для редактирования сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:message_detail')

    def get_context_data(self, **kwargs):
        """Переопределенный метод добавляет пользовательские данные в контекст,
        который передаётся в шаблон при рендеринге"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Редактирование сообщения: {self.object.subject}"
        return context


class MessageDetailView(DetailView):
    """Класс просмотра отдельного сообщения"""
    model = Message
    template_name = 'mailings/message_detail.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class MessageDeleteView(DeleteView):
    """Класс удаления отдельного сообщения"""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class MessageListView(ListView):
    model = Message
    template_name = "mailings/message_list.html"
    context_object_name = 'messages'

    def get_queryset(self):
        return get_cached_messages(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cache_enabled'] = getattr(settings, 'CACHE_ENABLED', False)
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Класс для создания рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    # try:
    #     send_mail(...)
    #     Recipient.objects.create(date=str(datetime.now()), status="Успешно", mailing=mailing)
    # except Exception as e:
    #     Recipient.objects.create(date=str(datetime.now()), status="Ошибка", answer_server=str(e), mailing=mailing)


class MailingUpdateView(OwnerOrManagerMixin, UpdateView):
    """Класс для редактирования получателя рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:mailing_detail')

    def get_context_data(self, **kwargs):
        """Переопределенный метод добавляет пользовательские данные в контекст,
        который передаётся в шаблон при рендеринге"""
        context = super().get_context_data(**kwargs)
        context['title'] = f"Редактирование рассылки: {self.object.datetime_start}"
        return context


class MailingDetailView(OwnerOrManagerMixin, DetailView):
    """Класс просмотра отдельного сообщения"""
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class MailingDeleteView(OwnerOrManagerMixin, DeleteView):
    """Класс удаления отдельного сообщения"""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('mailings:home')


class MailingDisableView(ManagerRequiredMixin, View):
    """Отключение рассылки (только для менеджеров)"""
    permission_required = 'mailings.block_mailing'

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status_mailing = Mailing.BLOCKED
        mailing.save()
        messages.success(request, f"Рассылка #{mailing.id} отключена")
        return redirect('mailings:mailing_detail', pk=pk)


class MailingListView(OwnerOrManagerMixin, ListView):
    model = Mailing
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.has_perm('mailings.view_all_mailings'):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner_mailing=self.request.user)


class MailingBlockView(UpdateView):
    """Блокировка рассылки"""
    model = Mailing
    fields = []  # Никаких полей не редактируем
    template_name = 'mailings/mailing_confirm_block.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        """Обновляем статус рассылки"""
        self.object = form.save(commit=False)
        self.object.status_mailing = Mailing.BLOCKED
        self.object.save()
        return super().form_valid(form)


class SendMailingView(LoginRequiredMixin, View):
    """Отправляет рассылку вручную"""
    login_url = reverse_lazy('users:login')
    template_name = 'mailings/mailing_confirm_send.html'

    def get(self, request, pk):
        """Показывает страницу подтверждения отправки"""
        mailing = get_object_or_404(Mailing, pk=pk)
        context = {'mailing': mailing}
        return render(request, self.template_name, context)

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Просто вызываем метод без распаковки
        try:
            success = mailing.send_messages()
            if success:
                messages.success(request, "Рассылка успешно отправлена!")
            else:
                messages.warning(request, "Не удалось начать рассылку: нет сообщения или получателей")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке: {str(e)}")

        return redirect('mailings:mailing_detail', pk=pk)


class HomePageView(TemplateView):
    """Контроллер главной страницы со статистикой рассылок"""
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Статистика рассылок
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(
            status_mailing=Mailing.LAUNCHED_AT
        ).count()
        context['unique_recipients'] = Recipient.objects.distinct().count()

        # Статистика попыток
        if user.is_authenticated:
            attempts = MailingAttempt.objects.filter(owner_attempt=user)

            context['total_attempts'] = attempts.count()
            context['success_attempts'] = attempts.filter(
                status_attempt=MailingAttempt.SUCCESSFULLY
            ).count()
            context['error_attempts'] = attempts.filter(
                status_attempt=MailingAttempt.UNSUCCESSFULLY
            ).count()

            # Последние 5 попыток
            context['recent_attempts'] = attempts.select_related(
                'mailing', 'recipient'
            ).order_by('-datetime_attempt')[:5]
        else:
            context['total_attempts'] = 0
            context['success_attempts'] = 0
            context['error_attempts'] = 0
            context['recent_attempts'] = []

        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailings/attempts_list.html'
    context_object_name = 'attempts'
    paginate_by = 10

    def get_queryset(self):
        queryset = MailingAttempt.objects.all()

        # Для менеджеров - все попытки
        if self.request.user.has_perm('mailings.view_all_mailings'):
            return queryset

        # Для пользователей - только их попытки
        return queryset.filter(
            owner_attempt=self.request.user
        ).select_related('mailing', 'recipient')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем список рассылок для фильтра
        context['mailings'] = Mailing.objects.filter(
            owner_mailing=self.request.user
        )

        # Сохраняем выбранную рассылку для фильтра
        context['selected_mailing'] = self.request.GET.get('mailing_id')

        return context


class MailingAttemptDetailView(DetailView):
    """Детальный просмотр попытки рассылки"""
    model = MailingAttempt
    template_name = 'mailings/attempt_detail.html'
    context_object_name = 'attempt'

    def get_queryset(self):
        return MailingAttempt.objects.filter(owner_attempt=self.request.user)
