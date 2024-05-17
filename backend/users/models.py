from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=150,
        verbose_name='Электронная почта',
        help_text='Введите электронную почту.',
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Никнейм',
        help_text='Введите никнейм.',
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя.',
        unique=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите фамилию.',
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_email_username',
            )
        ]

    def __str__(self):
        return f'{self.email} - {self.username}.'


class Subscription(models.Model):
    """Модель подписок."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
        help_text='Выберите автора рецепта.',
    )
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Выберите подписчика.',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'subscriber'),
                name='unique_author_subscriber',
            )
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}.'
