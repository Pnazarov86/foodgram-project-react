from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """Статус пользователей."""
    ADMIN = 'admin', 'Администратор'
    USER = 'user', 'Пользователь'


class User(AbstractUser):
    """Модель пользователей."""
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email пользователя'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин'
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    role = models.CharField(
        max_length=30,
        verbose_name='Статус пользователя',
        choices=UserRole.choices,
        default=UserRole.USER
    )

    @property
    def is_admin(self):
        return (
            self.role == UserRole.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    class Meta:
        ordering = ('role', 'id')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def str(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
