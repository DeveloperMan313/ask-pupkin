from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.urls.exceptions import Http404
from .models import *


def paginate(request, object_list):
    try:
        limit = int(request.GET.get('limit', 10))
    except ValueError:
        limit = 10
    if limit > 100:
        limit = 10
    try:
        num_page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(object_list, limit)
    try:
        page = paginator.page(num_page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def handler404(request, exception, template_name="404.html"):
    return render(
        request,
        template_name,
        status=404,
        context={
            'page_title': 'AskPupkin',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': True,
        },
    )


def index(request):
    page = paginate(request, Question.objects.new())
    for q in page.object_list:
        q.init_tag_list()
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'page': page,
            'is_logged_in': True,
            'questions': page.object_list,
            'category': 'new',
        },
    )


def hot(request):
    page = paginate(request, Question.objects.hot())
    for q in page.object_list:
        q.init_tag_list()
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin - Hot',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'page': page,
            'is_logged_in': True,
            'questions': page.object_list,
            'category': 'top',
        },
    )


def tag(request, tag):
    page = paginate(request, Question.objects.by_tag_name(tag))
    for q in page.object_list:
        q.init_tag_list()
    return render(
        request,
        'tag.html',
        context={
            'page_title': f'AskPupkin - Tag: {tag}',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'page': page,
            'is_logged_in': True,
            'tag': tag,
            'questions': page.object_list,
        },
    )


def ask(request):
    return render(
        request,
        'ask.html',
        context={
            'page_title': 'AskPupkin - Ask',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': True,
        },
    )


def question(request, question_id):
    question = Question.objects.by_id(question_id)
    question.init_tag_list()
    return render(
        request,
        'question.html',
        context={
            'page_title': 'AskPupkin - Question',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': True,
            'question': question,
            'answers': tuple(Answer.objects.by_question_id(question_id)),
        },
    )


def settings(request):
    return render(
        request,
        'settings.html',
        context={
            'page_title': 'AskPupkin - Settings',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': True,
        },
    )


def signup(request):
    return render(
        request,
        'signup.html',
        context={
            'page_title': 'AskPupkin - Sign Up',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': False,
        },
    )


def login(request):
    return render(
        request,
        'login.html',
        context={
            'page_title': 'AskPupkin - Log In',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'is_logged_in': False,
        },
    )
