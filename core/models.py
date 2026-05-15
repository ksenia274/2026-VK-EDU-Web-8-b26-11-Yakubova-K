import os
import uuid
from django.db import models


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'avatars/{uuid.uuid4()}{ext}'


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True, verbose_name='Аватар')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/avatar.png'
