from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AnswerForm, AskForm, CorrectAnswerForm, VoteForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag

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

    user_vote_question = None
    if request.user.is_authenticated:
        ql = QuestionLike.objects.filter(question=q, user=request.user).first()
        user_vote_question = ql.value if ql else None

        user_answer_vote = AnswerLike.objects.filter(
            user=request.user,
            answer=OuterRef('pk'),
        ).values('value')[:1]
        answers_qs = answers_qs.annotate(user_vote=Subquery(user_answer_vote))

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
    return render(request, 'questions/question.html', {
        'question': q,
        'answers': page,
        'form': form,
        'user_vote_question': user_vote_question,
    })


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


@require_POST
def like_question(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not_authenticated', 'login_url': '/login/'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'errors': form.errors}, status=400)

    question_id = form.cleaned_data['id']
    new_value = form.get_vote_value()

    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    with transaction.atomic():
        existing = QuestionLike.objects.filter(question=q, user=request.user).first()
        if existing:
            if existing.value == new_value:
                q.rating -= existing.value
                existing.delete()
                user_vote = None
            else:
                q.rating += new_value - existing.value
                existing.value = new_value
                existing.save(update_fields=['value'])
                user_vote = new_value
        else:
            QuestionLike.objects.create(question=q, user=request.user, value=new_value)
            q.rating += new_value
            user_vote = new_value
        q.save(update_fields=['rating'])

    return JsonResponse({'rating': q.rating, 'user_vote': user_vote})


@require_POST
def like_answer(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not_authenticated', 'login_url': '/login/'}, status=401)

    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'errors': form.errors}, status=400)

    answer_id = form.cleaned_data['id']
    new_value = form.get_vote_value()

    try:
        ans = Answer.objects.get(pk=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)

    with transaction.atomic():
        existing = AnswerLike.objects.filter(answer=ans, user=request.user).first()
        if existing:
            if existing.value == new_value:
                ans.rating -= existing.value
                existing.delete()
                user_vote = None
            else:
                ans.rating += new_value - existing.value
                existing.value = new_value
                existing.save(update_fields=['value'])
                user_vote = new_value
        else:
            AnswerLike.objects.create(answer=ans, user=request.user, value=new_value)
            ans.rating += new_value
            user_vote = new_value
        ans.save(update_fields=['rating'])

    return JsonResponse({'rating': ans.rating, 'user_vote': user_vote})


@require_POST
def mark_correct(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not_authenticated', 'login_url': '/login/'}, status=401)

    form = CorrectAnswerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'invalid_data', 'errors': form.errors}, status=400)

    question_id = form.cleaned_data['question_id']
    answer_id = form.cleaned_data['answer_id']

    try:
        q = Question.objects.select_related('author').get(pk=question_id)
    except Question.DoesNotExist:
        return JsonResponse({'error': 'question_not_found'}, status=404)

    if q.author != request.user:
        return JsonResponse({'error': 'not_author'}, status=403)

    try:
        ans = Answer.objects.get(pk=answer_id, question=q)
    except Answer.DoesNotExist:
        return JsonResponse({'error': 'answer_not_found'}, status=404)

    with transaction.atomic():
        if ans.is_correct:
            ans.is_correct = False
            ans.save(update_fields=['is_correct'])
            is_correct = False
        else:
            q.answers.filter(is_correct=True).update(is_correct=False)
            ans.is_correct = True
            ans.save(update_fields=['is_correct'])
            is_correct = True

    return JsonResponse({'is_correct': is_correct, 'answer_id': answer_id})
