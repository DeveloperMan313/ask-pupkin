from django.shortcuts import render, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.urls.exceptions import Http404
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
import json
from app import centrifugo
from .models import *
from .forms import *


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
        },
    )


@csrf_protect
def index(request):
    page = paginate(request, Question.objects.new().with_user_rating(request.user))
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
            'questions': page.object_list,
            'category': 'new',
        },
    )


@csrf_protect
def hot(request):
    page = paginate(request, Question.objects.hot().with_user_rating(request.user))
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
            'questions': page.object_list,
            'category': 'hot',
        },
    )


@csrf_protect
def tag(request, tag):
    questions = Question.objects.by_tag_name(tag).with_user_rating(request.user)
    if len(questions) == 0:
        raise Http404
    page = paginate(request, questions)
    for q in page.object_list:
        q.init_tag_list()
    return render(
        request,
        'index.html',
        context={
            'page_title': f'AskPupkin - Tag: {tag}',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'page': page,
            'tag': tag,
            'questions': page.object_list,
            'category': 'tag',
        },
    )


@csrf_protect
@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(user=request.user, data=request.POST)
        if form.is_valid():
            question_id = form.save()
            return HttpResponseRedirect(f'/question/{question_id}')
    else:
        form = QuestionForm()

    return render(
        request,
        'ask.html',
        context={
            'page_title': 'AskPupkin - Ask',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'form': form,
        },
    )


@csrf_protect
def question(request, question_id):
    try:
        question = Question.objects.with_user_rating(request.user).by_id(question_id)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = AnswerForm(user=request.user, question=question, data=request.POST)
        if form.is_valid():
            answer_id = form.save()
            centrifugo.publish_answer(question_id, Answer.objects.get(pk=answer_id))
            return HttpResponseRedirect(f'/question/{question_id}/#answer{answer_id}')
    else:
        form = AnswerForm()

    question.init_tag_list()
    return render(
        request,
        'question.html',
        context={
            'page_title': 'AskPupkin - Question',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'question': question,
            'answers': Answer.objects.by_question_id(question_id).with_user_rating(
                request.user
            ),
            'centrifugo': centrifugo.get_centrifugo_user_info(request.user.pk),
            'form': form,
        },
    )


@csrf_protect
@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/settings/')
    else:
        form = SettingsForm(user=request.user)

    return render(
        request,
        'settings.html',
        context={
            'page_title': 'AskPupkin - Settings',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'form': form,
        },
    )


@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()

    return render(
        request,
        'signup.html',
        context={
            'page_title': 'AskPupkin - Sign Up',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'form': form,
        },
    )


@csrf_protect
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()

    return render(
        request,
        'login.html',
        context={
            'page_title': 'AskPupkin - Log In',
            'popular_tags': Tag.objects.popular(),
            'best_members': Profile.objects.best(),
            'form': form,
        },
    )


@csrf_protect
def logout(request):
    if request.method != 'POST':
        return HttpResponseBadRequest
    auth_logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@csrf_protect
@login_required
def rate_question(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Wrong method')
    try:
        request_json = json.loads(request.body)
        if request_json['action'] not in ['like', 'dislike']:
            raise ValueError
        question = Question.objects.with_rating().get(pk=request_json['id'])
    except (ValueError, KeyError, ObjectDoesNotExist):
        return HttpResponseBadRequest('Wrong format')

    if question.user == request.user:
        return HttpResponseBadRequest('User cannot rate oneself')

    try:
        users_rating = QuestionRating.objects.get(user=request.user, question=question)
    except ObjectDoesNotExist:
        users_rating = None

    old_rating = question.rating
    is_like = request_json['action'] == 'like'

    if (
        users_rating is None
        or (not users_rating.is_positive and is_like)
        or (users_rating.is_positive and not is_like)
    ):
        if users_rating is None:
            QuestionRating(
                user=request.user, question=question, is_positive=is_like
            ).save()
        else:
            users_rating.delete()

        if is_like:
            new_rating = old_rating + 1
        else:
            new_rating = old_rating - 1
    else:
        new_rating = old_rating

    return JsonResponse({'new_rating': new_rating})


@csrf_protect
@login_required
def rate_answer(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Wrong method')
    try:
        request_json = json.loads(request.body)
        if request_json['action'] not in ['like', 'dislike']:
            raise ValueError
        answer = Answer.objects.with_rating().get(pk=request_json['id'])
    except (ValueError, KeyError, ObjectDoesNotExist):
        return HttpResponseBadRequest('Wrong format')

    if answer.user == request.user:
        return HttpResponseBadRequest('User cannot rate oneself')

    try:
        users_rating = AnswerRating.objects.get(user=request.user, answer=answer)
    except ObjectDoesNotExist:
        users_rating = None

    old_rating = answer.rating
    is_like = request_json['action'] == 'like'

    if (
        users_rating is None
        or (not users_rating.is_positive and is_like)
        or (users_rating.is_positive and not is_like)
    ):
        if users_rating is None:
            AnswerRating(user=request.user, answer=answer, is_positive=is_like).save()
        else:
            users_rating.delete()

        if is_like:
            new_rating = old_rating + 1
        else:
            new_rating = old_rating - 1
    else:
        new_rating = old_rating

    return JsonResponse({'new_rating': new_rating})


@csrf_protect
@login_required
def answer_correct_set(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Wrong method')
    try:
        request_json = json.loads(request.body)
        if request_json['checked'] not in [True, False]:
            raise ValueError
        answer = Answer.objects.get(pk=request_json['id'])
    except (ValueError, KeyError, ObjectDoesNotExist):
        return HttpResponseBadRequest('Wrong format')

    if request.user != answer.question.user:
        return HttpResponseBadRequest(
            'Cannot mark correct answer under other user\'s question'
        )

    answer.is_correct = request_json['checked']
    answer.save()

    return HttpResponse()
