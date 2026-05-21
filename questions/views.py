from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, AskForm
from .models import Question, Tag

ANSWERS_PER_PAGE = 5


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
    answers_qs = q.answers.select_related('author', 'author__profile').order_by('-is_correct', '-rating', 'pk')

    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(question=q, author=request.user)
            all_pks = list(answers_qs.values_list('pk', flat=True))
            position = all_pks.index(answer.pk)
            page_num = position // ANSWERS_PER_PAGE + 1
            return redirect(f'{q.get_url()}?page={page_num}#answer-{answer.pk}')
    else:
        form = AnswerForm()

    page = paginate(answers_qs, request, per_page=ANSWERS_PER_PAGE)
    return render(request, 'questions/question.html', {'question': q, 'answers': page, 'form': form})


@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            new_question = form.save(author=request.user)
            return redirect('question', question_id=new_question.pk)
    else:
        form = AskForm()
    return render(request, 'questions/ask.html', {'form': form})
