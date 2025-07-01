from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс для создания модели пользователя с заданными полями"""
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    phone = models.CharField(
        max_length=35, verbose_name="Телефон", blank=True, null=True, help_text="Введите номер телефона"
    )
    country = models.CharField(max_length=50, verbose_name="Страна", blank=True, null=True, help_text="Введите страну")
    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True, help_text="Загрузите аватар"
    )
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован",
        help_text="Пользователь заблокирован менеджером"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        """Meta класс, который задает конфигурационные параметры"""
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("blocked_users", "Может блокировать пользователей"),
            ("view_all_users", "Может просматривать всех пользователей"),
        ]

    def __str__(self):
        """Строковое представление класса"""
        return self.email
