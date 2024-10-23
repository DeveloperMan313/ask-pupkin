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
    for i in range(1, 5)
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


def index(request):
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin',
            'is_logged_in': True,
            'questions': QUESTIONS,
            'category': 'new',
        },
    )


def hot(request):
    return render(
        request,
        'index.html',
        context={
            'page_title': 'AskPupkin - Hot',
            'is_logged_in': True,
            'questions': reversed(QUESTIONS),
            'category': 'top',
        },
    )


def ask(request):
    return render(
        request,
        'ask.html',
        context={
            'page_title': 'AskPupkin - Ask',
            'is_logged_in': True,
        },
    )


def question(request, question_id):
    return render(
        request,
        'question.html',
        context={
            'page_title': 'AskPupkin - Question',
            'is_logged_in': True,
            'question': next(filter(lambda q: q['id'] == question_id, QUESTIONS)),
            'answers': ANSWERS,
        },
    )
