from django import forms
from django.utils.text import slugify

from .models import Answer, Question, Tag


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=False,
        max_length=200,
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        labels = {
            'title': 'Заголовок',
            'content': 'Описание',
        }

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author
        if commit:
            question.save()
            tags_input = self.cleaned_data.get('tags', '')
            for raw in tags_input.split(','):
                slug = slugify(raw.strip(), allow_unicode=True)
                if slug:
                    tag, _ = Tag.objects.get_or_create(name=slug)
                    question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {'content': 'Ответ'}

    def save(self, question, author, commit=True):
        answer = super().save(commit=False)
        answer.question = question
        answer.author = author
        if commit:
            answer.save()
            question.answers_count += 1
            question.save(update_fields=['answers_count'])
        return answer
