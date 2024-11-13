from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import *
from random import choice, choices, randint


COMMON_WORDS = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make',
                'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us']


def random_text(min_words: int, max_words: int) -> str:
    return ' '.join(choices(COMMON_WORDS, k=randint(min_words, max_words)))


def fill_profiles(count: int):
    users = []
    profiles = []
    for i in range(count):
        user = User(username=f'user_{i}')
        users.append(user)
        profiles.append(Profile(user=user, nickname=f'User {i}'))
    User.objects.bulk_create(users)
    Profile.objects.bulk_create(profiles)

    print('profiles filled')


def fill_tags(count: int):
    tags = [Tag(name=choice(COMMON_WORDS)) for _ in range(count)]
    Tag.objects.bulk_create(tags)

    print('tags filled')


def fill_questions(count: int):
    users = tuple(User.objects.all())
    tags = tuple(Tag.objects.all())
    questions = []
    for _ in range(count):
        user = choice(users)
        title = random_text(2, 5)
        text = random_text(10, 100)
        questions.append(Question(user=user, title=title, text=text))
    Question.objects.bulk_create(questions)
    for question in questions:
        question.tags.set(choices(tags, k=randint(0, 5)))
        question.save()

    print('questions filled')


def fill_answers(count: int):
    users = tuple(User.objects.all())
    questions = tuple(Question.objects.all())
    answers = []
    for _ in range(count):
        user = choice(users)
        question = choice(questions)
        text = random_text(5, 50)
        answers.append(Answer(user=user, question=question,
                       text=text, is_correct=randint(0, 1)))
    Answer.objects.bulk_create(answers)

    print('answers filled')


def fill_question_ratings(count: int):
    users = set(User.objects.all())
    questions = tuple(Question.objects.all())
    q_ratings = []
    user_can_rate = {u: set(questions) for u in users}
    for _ in range(count):
        user = choice(tuple(users))
        question = choice(tuple(user_can_rate[user]))
        user_can_rate[user].remove(question)
        if len(user_can_rate) == 0:
            users.remove(user)
        q_ratings.append(QuestionRating(
            user=user, question=question, is_positive=randint(0, 1)))
    QuestionRating.objects.bulk_create(q_ratings)

    print('question ratings filled')


def fill_answer_ratings(count: int):
    users = set(User.objects.all())
    answers = tuple(Answer.objects.all())
    a_ratings = []
    user_can_rate = {u: set(answers) for u in users}
    for _ in range(count):
        user = choice(tuple(users))
        answer = choice(tuple(user_can_rate[user]))
        user_can_rate[user].remove(answer)
        if len(user_can_rate) == 0:
            users.remove(user)
        a_ratings.append(AnswerRating(
            user=user, answer=answer, is_positive=randint(0, 1)))
    AnswerRating.objects.bulk_create(a_ratings)

    print('answer ratings filled')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--ratio', type=int)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if kwargs['ratio'] is None:
            print('Please, supply --ratio [RATIO]')
            return
        ratio = kwargs['ratio']

        fill_profiles(ratio)
        fill_tags(ratio)
        fill_questions(ratio * 10)
        fill_answers(ratio * 100)
        fill_question_ratings(ratio * 100)
        fill_answer_ratings(ratio * 100)

        print('database filled')
