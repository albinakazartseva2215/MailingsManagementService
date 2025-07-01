import logging
from mailings.models import Message

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_cached_messages(user):
    """
    Получает закешированный список сообщений для пользователя.
    Если данные не в кэше, загружает из БД и кэширует.
    """
    # Генерируем ключ с учётом прав пользователя
    cache_key = f"messages_{'all' if user.has_perm('mailings.view_all_messages') else user.pk}"

    # Логирование для отладки
    logger.debug(f"Cache key: {cache_key}, CACHE_ENABLED: {settings.CACHE_ENABLED}")

    if not settings.CACHE_ENABLED:
        logger.debug("Cache disabled, fetching from DB")
        return fetch_messages_from_db(user)

    # Пытаемся получить из кэша
    messages = cache.get(cache_key)

    if messages is not None:
        logger.debug("Cache hit")
        return messages

    logger.debug("Cache miss, fetching from DB")
    messages = fetch_messages_from_db(user)

    # Сохраняем в кэш с таймаутом
    try:
        cache.set(cache_key, messages, timeout=300)
        logger.debug(f"Cache set for key: {cache_key}")
    except Exception as e:
        logger.error(f"Cache set error: {e}")

    return messages


def fetch_messages_from_db(user):
    """Получает сообщения из БД с оптимизацией"""
    queryset = Message.objects.select_related('owner_message').only(
        'id', 'subject', 'body', 'owner_message'
    )

    if user.has_perm('mailings.view_all_messages'):
        return list(queryset.all())  # Преобразуем в list для кэширования
    return list(queryset.filter(owner_message=user))
