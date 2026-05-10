from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Question, Tag
from django.contrib.auth.models import User


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)
    return page


def sidebar_context():
    tags = Tag.objects.order_by('name')[:20]
    best_members = User.objects.order_by('-date_joined').select_related('profile')[:5]
    return {'tags': tags, 'best_members': best_members}


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {
        'questions': page, 'page_title': 'Новые вопросы', **sidebar_context()
    })


def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {
        'questions': page, 'page_title': 'Лучшие вопросы', **sidebar_context()
    })


def tag(request, tag_name):
    get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = paginate(questions, request)
    return render(request, 'questions/index.html', {
        'questions': page,
        'page_title': f'Вопросы по тегу: {tag_name}',
        'current_tag': tag_name,
        **sidebar_context(),
    })


def question(request, question_id):
    q = get_object_or_404(
        Question.objects.select_related('author', 'author__profile').prefetch_related('tags'),
        pk=question_id,
    )
    answers = q.answers.select_related('author', 'author__profile').order_by('-is_correct', '-rating')
    page = paginate(answers, request, per_page=5)
    return render(request, 'questions/question.html', {
        'question': q, 'answers': page, **sidebar_context()
    })


def ask(request):
    return render(request, 'questions/ask.html', sidebar_context())
