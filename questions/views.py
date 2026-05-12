from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Question, Tag


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)
    return page


def index(request):
    page = paginate(Question.objects.new(), request)
    return render(request, 'questions/index.html', {'questions': page, 'page_title': 'Новые вопросы'})


def hot(request):
    page = paginate(Question.objects.hot(), request)
    return render(request, 'questions/index.html', {'questions': page, 'page_title': 'Лучшие вопросы'})


def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    page = paginate(Question.objects.by_tag(tag_name), request)
    return render(request, 'questions/index.html', {
        'questions': page,
        'page_title': f'Вопросы по тегу: {tag_name}',
        'current_tag': tag_name,
    })


def question(request, question_id):
    q = get_object_or_404(
        Question.objects.select_related('author', 'author__profile').prefetch_related('tags'),
        pk=question_id,
    )
    answers = q.answers.select_related('author', 'author__profile').order_by('-is_correct', '-rating')
    page = paginate(answers, request, per_page=5)
    return render(request, 'questions/question.html', {'question': q, 'answers': page})


def ask(request):
    return render(request, 'questions/ask.html')
