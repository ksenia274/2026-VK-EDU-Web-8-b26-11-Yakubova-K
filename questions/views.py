from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


TAGS = ['python', 'django', 'javascript', 'css', 'html', 'react', 'sql', 'git']

BEST_MEMBERS = [
    {'username': 'alice'},
    {'username': 'bob'},
    {'username': 'charlie'},
    {'username': 'dave'},
    {'username': 'eve'},
]


def generate_questions(count=29):
    questions = []
    for i in range(1, count + 1):
        questions.append({
            'id': i,
            'title': f'Question title number {i}',
            'text': f'This is the body text of question {i}. It describes the problem in detail.',
            'author': f'user{i % 5 + 1}',
            'answers_count': i % 7,
            'tags': [TAGS[i % len(TAGS)], TAGS[(i + 2) % len(TAGS)]],
            'votes': i * 3,
        })
    return questions


def generate_answers(count=5):
    answers = []
    for i in range(1, count + 1):
        answers.append({
            'id': i,
            'text': f'Answer number {i}: here is a detailed explanation to your question.',
            'author': f'user{i}',
            'votes': i * 2,
            'is_correct': i == 1,
        })
    return answers


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def index(request):
    questions = generate_questions(29)
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {
        'questions': page,
        'tags': TAGS,
        'best_members': BEST_MEMBERS,
        'page_title': 'New Questions',
    })


def hot(request):
    questions = sorted(generate_questions(29), key=lambda q: q['votes'], reverse=True)
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {
        'questions': page,
        'tags': TAGS,
        'best_members': BEST_MEMBERS,
        'page_title': 'Hot Questions',
    })


def tag(request, tag_name):
    all_questions = generate_questions(29)
    filtered = [q for q in all_questions if tag_name in q['tags']]
    page = paginate(filtered, request, per_page=10)
    return render(request, 'questions/index.html', {
        'questions': page,
        'tags': TAGS,
        'best_members': BEST_MEMBERS,
        'page_title': f'Questions tagged: {tag_name}',
        'current_tag': tag_name,
    })


def question(request, question_id):
    q = {
        'id': question_id,
        'title': f'Question title number {question_id}',
        'text': f'This is the body text of question {question_id}. It describes the problem in detail.',
        'author': f'user{question_id % 5 + 1}',
        'tags': [TAGS[question_id % len(TAGS)], TAGS[(question_id + 2) % len(TAGS)]],
        'votes': question_id * 3,
    }
    answers = generate_answers(5)
    page = paginate(answers, request, per_page=5)
    return render(request, 'questions/question.html', {
        'question': q,
        'answers': page,
        'tags': TAGS,
        'best_members': BEST_MEMBERS,
    })


def ask(request):
    return render(request, 'questions/ask.html', {
        'tags': TAGS,
        'best_members': BEST_MEMBERS,
    })
