from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new(self):
        return (
            self.select_related('author', 'author__profile')
            .prefetch_related('tags')
            .order_by('-created_at')
        )

    def hot(self):
        return (
            self.select_related('author', 'author__profile')
            .prefetch_related('tags')
            .order_by('-rating')
        )

    def by_tag(self, tag_name):
        return (
            self.filter(tags__name=tag_name)
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
            .order_by('-created_at')
        )


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    answers_count = models.IntegerField(default=0, verbose_name='Количество ответов')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse('question', args=[self.pk])


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    content = models.TextField(verbose_name='Текст')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'{self.author.username}: {self.question.title[:50]}'


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = ('question', 'user')

    def __str__(self):
        return f'{self.user.username} → вопрос #{self.question_id}'


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = ('answer', 'user')

    def __str__(self):
        return f'{self.user.username} → ответ #{self.answer_id}'
