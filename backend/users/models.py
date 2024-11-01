from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME


class User(AbstractUser):
    username = models.CharField(max_length=MAX_LENGTH_NAME, unique=True,
                                verbose_name='Логин пользователя')
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL,
                              unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=MAX_LENGTH_NAME,
                                 verbose_name='Фамилия')
    is_subscribed = models.BooleanField(default=False,
                                        verbose_name='Подписка на пользователя'
                                        )
    avatar = models.ImageField(verbose_name='Ссылка на аватар')
    password = models.TextField(verbose_name='пароль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.following
