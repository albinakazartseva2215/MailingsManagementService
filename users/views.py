import secrets

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, FormView, ListView, View

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserProfileForm, CustomSetPasswordForm, PasswordResetRequestForm
from users.models import User
from utils.mixins import ManagerRequiredMixin


class PasswordResetRequestView(FormView):
    """Класс для запроса сброса пароля"""
    template_name = 'users/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            token = secrets.token_hex(16)
            user.token = token
            user.save()

            host = self.request.get_host()
            reset_url = f"http://{host}{reverse('users:password_reset_confirm', kwargs={'token': token})}"

            send_mail(
                subject="Восстановление пароля",
                message=f"Для сброса пароля перейдите по ссылке: {reset_url}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email]
            )

        messages.info(self.request, "Если аккаунт с таким email существует, инструкции отправлены на почту")
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    """Класс для установки нового пароля"""
    template_name = 'users/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        """Этот метод выполняется первым при обработке запроса"""
        token = kwargs.get('token')
        self.user = User.objects.filter(token=token).first()

        if not self.user:
            messages.error(request, "Неверная или устаревшая ссылка")
            return redirect('users:password_reset')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Подготавливает аргументы для создания формы"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        """Выполняется при успешной валидации формы"""
        form.save()
        self.user.token = None  # Очищаем токен после использования
        self.user.save()
        messages.success(self.request, "Пароль успешно изменён! Теперь вы можете войти")
        return super().form_valid(form)


class UserCreateView(CreateView):
    """Класс создания пользователя"""
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Метод переопределенный для регистрации пользователя с отправкой на почту ссылки для подтверждения"""
        user = form.save()
        user.is_active = False  # пользователь не сможет войти, пока не активирует аккаунт
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    """метод, который обрабатывает подтверждение email по токену"""
    user = get_object_or_404(User, token=token)
    user.is_active = True   # активирует учётную запись пользователя
    user.token = None   # очищаем токен после подтверждения
    user.save()
    return redirect(reverse("users:login"))


def user_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы")
    return redirect('/users/login/')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_blocked:
                messages.error(request, "Ваш аккаунт заблокирован менеджером")
                return render(request, 'users/login.html')

            login(request, user)
            return redirect('mailings:home')
        else:
            messages.error(request, "Неверный email или пароль")

    return render(request, 'users/login.html')


class UserListView(ManagerRequiredMixin, ListView):
    """Список пользователей (только для менеджеров)"""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    permission_required = 'users.view_all_users'

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)


class BlockUserView(ManagerRequiredMixin, View):
    """Блокировка/разблокировка пользователя"""
    permission_required = "users.block_user"

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_blocked = not user.is_blocked
        user.save()

        action = "заблокирован" if user.is_blocked else "разблокирован"
        messages.success(request, f"Пользователь {user.email} {action}")
        return redirect('mailings:user_list')


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Класс просмотра профиля пользователя"""
    model = User
    template_name = 'users/profile_detail.html'
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        """Возвращает профиль текущего пользователя"""
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Класс редактирования профиля пользователя"""
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        """Редактирование только своего профиля"""
        return self.request.user

    def form_valid(self, form):
        """Дополнительные действия при успешном обновлении"""
        response = super().form_valid(form)
        # Например, отправка уведомления
        messages.success(self.request, "Профиль успешно обновлён")
        return response
