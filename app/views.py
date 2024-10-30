from math import ceil
from django.shortcuts import render


QUESTIONS = [
    {
        'id': i,
        'title': f'Title {i}',
        'text': 'text ' * i,
        'answer_count': i,
        'tags': [f'tag{j}' for j in range(1, i + 1)],
        'likes': i,
    }
    for i in range(1, 23)
]

ANSWERS = [
    {
        'id': i,
        'text': 'text ' * i,
        'likes': i,
        'is_correct': i == 1,
    }
    for i in range(1, 5)
]

POPULAR_TAGS = [f'tag{i}' for i in range(1, 10)]

BEST_MEMBERS = [f'member{i}' for i in range(1, 4)]


def paginate(objects_list, request, per_page=5):
    try:
        page_num = int(request.GET['p'])
    except KeyError:
        page_num = 1
    except ValueError:
        page_num = 1
    num_pages = ceil(len(objects_list) / per_page)
    page_num = max(1, min(page_num, num_pages))
    page = objects_list[(page_num - 1) * per_page:page_num * per_page]
    return page_num, page, num_pages


def index(request):
    page_num, questions, num_pages = paginate(QUESTIONS, request)
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'page': page_num,
            'num_pages': num_pages,
            'is_logged_in': True,
            'questions': questions,
            'category': 'new',
        },
    )


def hot(request):
    page_num, questions, num_pages = paginate(
        tuple(reversed(QUESTIONS)), request)
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin - Hot',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'page': page_num,
            'num_pages': num_pages,
            'is_logged_in': True,
            'questions': questions,
            'category': 'top',
        },
    )


def tag(request, tag):
    page_num, questions, num_pages = paginate(
        tuple(filter(lambda q: tag in q['tags'], QUESTIONS)),
        request)
    return render(
        request,
        'tag.html',
        context={
            'page_title': f'AskPupkin - Tag: {tag}',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'page': page_num,
            'num_pages': num_pages,
            'is_logged_in': True,
            'tag': tag,
            'questions': questions,
        },
    )


def ask(request):
    return render(
        request,
        'ask.html',
        context={
            'page_title': 'AskPupkin - Ask',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'is_logged_in': True,
        },
    )


def question(request, question_id):
    return render(
        request,
        'question.html',
        context={
            'page_title': 'AskPupkin - Question',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'is_logged_in': True,
            'question': next(filter(lambda q: q['id'] == question_id, QUESTIONS)),
            'answers': ANSWERS,
        },
    )


def settings(request):
    return render(
        request,
        'settings.html',
        context={
            'page_title': 'AskPupkin - Settings',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'is_logged_in': True,
        },
    )


def signup(request):
    return render(
        request,
        'signup.html',
        context={
            'page_title': 'AskPupkin - Sign Up',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'is_logged_in': False,
        },
    )


def login(request):
    return render(
        request,
        'login.html',
        context={
            'page_title': 'AskPupkin - Log In',
            'popular_tags': POPULAR_TAGS,
            'best_members': BEST_MEMBERS,
            'is_logged_in': False,
        },
    )
