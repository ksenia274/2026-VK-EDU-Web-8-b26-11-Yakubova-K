import os

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Profile

ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB


def validate_avatar(avatar):
    if avatar:
        ext = os.path.splitext(avatar.name)[1].lower().lstrip('.')
        if ext not in ALLOWED_AVATAR_EXTENSIONS:
            allowed = ', '.join(sorted(ALLOWED_AVATAR_EXTENSIONS))
            raise forms.ValidationError(f'Недопустимый формат. Допустимые форматы: {allowed}.')
        if avatar.size > MAX_AVATAR_SIZE:
            raise forms.ValidationError('Файл слишком большой. Максимальный размер: 2 МБ.')
    return avatar


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Неверный логин или пароль.')
            if not user.is_active:
                raise forms.ValidationError('Аккаунт отключён.')
            cleaned_data['user'] = user
        return cleaned_data


class SignupForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_avatar(self):
        return validate_avatar(self.cleaned_data.get('avatar'))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                self.add_error('password2', 'Пароли не совпадают.')
            else:
                temp_user = User(
                    username=cleaned_data.get('username', ''),
                    email=cleaned_data.get('email', ''),
                )
                try:
                    validate_password(password, user=temp_user)
                except forms.ValidationError as e:
                    self.add_error('password', e)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar'),
            )
        return user


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label='Аватар', required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_avatar(self):
        return validate_avatar(self.cleaned_data.get('avatar'))

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            avatar = self.cleaned_data.get('avatar')
            if avatar:
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.avatar = avatar
                profile.save(update_fields=['avatar'])
        return user
