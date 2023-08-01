from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q

from users.constants import EMAIL_MAX_LEN, NAME_MAX_LEN

unique_username_validator = [UnicodeUsernameValidator()]


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_MAX_LEN,
        unique=True,
        verbose_name='Адрес эл. почты'
    )
    username = models.CharField(
        max_length=NAME_MAX_LEN,
        unique=True,
        verbose_name='Имя пользователя',
        validators=unique_username_validator
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LEN,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LEN,
        verbose_name='Фамилия'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                name='check_unable_to_subscribe_more_than_once',
                fields=['user', 'author']
            ),
            models.CheckConstraint(
                name='check_unable_to_self_subscribe',
                check=~Q(user=F('author'))
            ),
        ]
